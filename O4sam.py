import os
import cv2
import torch
import numpy as np
from tqdm import tqdm
from pathlib import Path
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

# -------------------------------
# Параметры (измените под себя)
# -------------------------------
INPUT_DIR = "input_images"      # папка с исходными фотографиями
OUTPUT_DIR = "output_masks"     # папка для сохранения результатов
MODEL_TYPE = "vit_b"            # "vit_b", "vit_l" или "vit_h"
CHECKPOINT_PATH = "sam_vit_b_01ec64.pth"   # путь к весам

# Параметры генератора масок (можно менять)
MASK_GENERATOR_KWARGS = {
    "points_per_side": 32,
    "pred_iou_thresh": 0.86,
    "stability_score_thresh": 0.92,
    "crop_n_layers": 1,
    "min_mask_region_area": 100,
}

# Форматы изображений, которые будем обрабатывать
SUPPORTED_EXT = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

# Сохранять ли визуализацию (маски поверх изображения)
SAVE_VISUALIZATION = True
# Сохранять ли все маски в виде отдельных файлов (словарь метаданных + бинарные маски)
SAVE_RAW_MASKS = True

# -------------------------------
# Инициализация модели (один раз)
# -------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Используется устройство: {device}")

print("Загрузка модели SAM...")
sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH)
sam.to(device=device)
mask_generator = SamAutomaticMaskGenerator(sam, **MASK_GENERATOR_KWARGS)
print("Модель загружена.")

# Создаём выходную папку, если её нет
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
vis_dir = os.path.join(OUTPUT_DIR, "visualizations")
if SAVE_VISUALIZATION:
    Path(vis_dir).mkdir(exist_ok=True)
masks_dir = os.path.join(OUTPUT_DIR, "raw_masks")
if SAVE_RAW_MASKS:
    Path(masks_dir).mkdir(exist_ok=True)

# -------------------------------
# Функция сохранения всех масок в удобном формате
# -------------------------------
def save_masks_as_npz(masks_list, output_path):
    """
    Сохраняет список масок (словарей) в один .npz файл.
    Каждая маска сохраняется как отдельный массив + метаданные.
    """
    if not masks_list:
        return
    # Подготовим данные для сохранения
    num_masks = len(masks_list)
    masks_arrays = []
    ious = []
    areas = []
    for idx, m in enumerate(masks_list):
        masks_arrays.append(m['segmentation'].astype(np.uint8))  # bool -> uint8
        ious.append(m['predicted_iou'])
        areas.append(m['area'])
    np.savez_compressed(
        output_path,
        masks=np.stack(masks_arrays, axis=0),
        predicted_iou=np.array(ious),
        area=np.array(areas),
        num_masks=num_masks
    )

def visualize_masks(image, masks_list, output_path):
    """Рисует все маски поверх изображения и сохраняет результат."""
    if len(masks_list) == 0:
        # Просто копируем исходное изображение
        cv2.imwrite(output_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return
    
    # Сортируем маски по площади (большие сверху для лучшего вида)
    sorted_masks = sorted(masks_list, key=lambda x: x['area'], reverse=True)
    # Создаём изображение с прозрачным слоем
    overlay = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
    
    for mask_dict in sorted_masks:
        mask = mask_dict['segmentation']
        # Случайный цвет (RGB) + непрозрачность 0.6
        color = np.random.randint(0, 255, 3, dtype=np.uint8)
        alpha = 150  # 0..255
        for c in range(3):
            overlay[mask, c] = color[c]
        overlay[mask, 3] = alpha
    
    # Накладываем на исходное изображение
    image_rgba = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
    # Композитинг: результат = фон * (1 - a) + overlay * a (простой)
    result = image_rgba.copy().astype(np.float32)
    overlay_f = overlay.astype(np.float32) / 255.0
    result_f = result.astype(np.float32) / 255.0
    alpha_mask = overlay_f[:, :, 3:4]
    combined = result_f * (1 - alpha_mask) + overlay_f[:, :, :3] * alpha_mask
    combined = (combined * 255).astype(np.uint8)
    
    # Сохраняем как BGR для OpenCV
    cv2.imwrite(output_path, cv2.cvtColor(combined, cv2.COLOR_RGBA2BGR))

# -------------------------------
# Основной цикл обработки
# -------------------------------
def process_image(image_path):
    """Обрабатывает одно изображение: генерирует маски и сохраняет."""
    # Загрузка
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print(f"  Ошибка: не удалось прочитать {image_path}")
        return False
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Генерация масок (автоматическая)
    masks = mask_generator.generate(img_rgb)
    print(f"  Сгенерировано {len(masks)} масок")
    
    basename = Path(image_path).stem
    
    # Сохраняем сырые маски, если нужно
    if SAVE_RAW_MASKS and masks:
        npz_path = os.path.join(masks_dir, f"{basename}_masks.npz")
        save_masks_as_npz(masks, npz_path)
    
    # Сохраняем визуализацию, если нужно
    if SAVE_VISUALIZATION:
        vis_path = os.path.join(vis_dir, f"{basename}_vis.jpg")
        visualize_masks(img_rgb, masks, vis_path)
    
    return True

# Получаем список всех изображений в INPUT_DIR
image_files = []
for ext in SUPPORTED_EXT:
    image_files.extend(Path(INPUT_DIR).glob(f"*{ext}"))
    image_files.extend(Path(INPUT_DIR).glob(f"*{ext.upper()}"))

print(f"Найдено {len(image_files)} изображений в папке '{INPUT_DIR}'.")
if not image_files:
    print("Нет изображений для обработки. Проверьте путь INPUT_DIR.")
    exit(0)

# Обработка с прогресс-баром
for img_path in tqdm(image_files, desc="Обработка изображений"):
    process_image(str(img_path))

print(f"\nГотово! Результаты сохранены в '{OUTPUT_DIR}'.")
print(f"  - Визуализации: {vis_dir if SAVE_VISUALIZATION else 'не сохранены'}")
print(f"  - Сырые маски (.npz): {masks_dir if SAVE_RAW_MASKS else 'не сохранены'}")
