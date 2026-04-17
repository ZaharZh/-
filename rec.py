import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk, ImageFilter, ImageEnhance
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Используем ту же модель
device = torch.device("cpu")
processor = TrOCRProcessor.from_pretrained("kazars24/trocr-base-handwritten-ru")
model = VisionEncoderDecoderModel.from_pretrained("kazars24/trocr-base-handwritten-ru")
model.eval()
model.to(device)

# Глобальные переменные для рисования
drawing_img = None
draw = None
canvas_photo = None

def init_drawing(width=400, height=400):
    """Инициализация белого холста для рисования"""
    global drawing_img, draw, canvas_photo
    drawing_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(drawing_img)
    update_canvas_display()

def update_canvas_display():
    """Обновляет отображение на Canvas"""
    global canvas_photo
    canvas_photo = ImageTk.PhotoImage(drawing_img)
    canvas.create_image(0, 0, image=canvas_photo, anchor="nw")
    canvas.image = canvas_photo

def preprocess_for_trocr(pil_img: Image.Image) -> Image.Image:
    """Предобработка изображения для модели TrOCR"""
    img = pil_img.convert("L")                     # оттенки серого
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.2)                    # повышение контраста
    img = img.filter(ImageFilter.GaussianBlur(1.0)) # небольшое размытие
    return img.convert("RGB")                      # TrOCR ожидает RGB

def recognize():
    """Распознавание нарисованного символа"""
    if drawing_img is None:
        result_var.set("Нет изображения")
        return

    processed = preprocess_for_trocr(drawing_img)

    try:
        # Подготовка тензора
        pixel_values = processor(images=processed, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        # Инференс
        with torch.no_grad():
            generated_ids = model.generate(pixel_values)

        # Декодирование результата
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)
        recognized = text[0] if text else "?"

        result_var.set(recognized)

    except Exception as e:
        result_var.set(f"Ошибка: {str(e)[:40]}")

def paint(event):
    """Рисование кистью при движении мыши"""
    x, y = event.x, event.y
    r = brush_size
    draw.ellipse((x - r, y - r, x + r, y + r), fill="black", outline="black")
    update_canvas_display()

def clear_canvas():
    """Очистка холста и сброс результата"""
    init_drawing()
    result_var.set("")

# Создание основного окна
root = tk.Tk()
root.title("Распознавание рукописных символов")
root.geometry("600x550")
root.resizable(False, False)

# Поле для рисования
canvas = tk.Canvas(root, width=400, height=400, bg="white", highlightthickness=2, relief="ridge")
canvas.pack(pady=20)
canvas.bind("<B1-Motion>", paint)

brush_size = 20

# Кнопки управления
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

btn_recognize = tk.Button(btn_frame, text="Определить", command=recognize, width=15, font=("Arial", 12))
btn_recognize.pack(side="left", padx=20)

btn_clear = tk.Button(btn_frame, text="Очистить", command=clear_canvas, width=15, font=("Arial", 12))
btn_clear.pack(side="left", padx=20)

# Поле для вывода результата
result_frame = tk.LabelFrame(root, text="Результат распознавания", font=("Arial", 12))
result_frame.pack(pady=15, padx=20, fill="x")

result_var = tk.StringVar()
result_var.set("")
result_label = tk.Label(result_frame, textvariable=result_var, font=("Arial", 24, "bold"), fg="blue")
result_label.pack(pady=15, padx=10)

# Запуск интерфейса
init_drawing()
root.mainloop()
