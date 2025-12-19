import cv2
import numpy as np
from skimage.feature import local_binary_pattern
import matplotlib.pyplot as plt

def extract_lbp_features():
  # ЭТАП 1: Загрузка и конвертация в оттенки серого
  image = cv2.imread(‘image.jpeg’)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  print(f"Изображение загружено. Размер: {gray.shape}")
  
  # ЭТАП 2: Вычисление карты LBP
  P=8
  R=1
  lbp = local_binary_pattern(gray, P, R, method='uniform’)
  print(f"Карта LBP вычислена. Уникальных меток: {np.unique(lbp).size}")
  
  # ЭТАП 3: Построение гистограммы
  # Для uniform patterns: количество бинов = P*(P-1) + 3
  n_bins = P * (P - 1) + 3 if method == 'uniform' else (2**P)
  hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins))
  # Нормализация гистограммы
  hist = hist.astype("float")
  hist /= (hist.sum() + 1e-7

  # ЭТАП 4: Визуализация
  fig, axes = plt.subplots(1, 3, figsize=(15, 5))
  axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
  axes[0].set_title('Исходное изображение')
  axes[0].axis('off')

  axes[1].imshow(lbp, cmap='gray')
  axes[1].set_title(f'Карта LBP (P={P}, R={R})')
  axes[1].axis('off')

  axes[2].plot(hist)
  axes[2].set_title('Нормализованная гистограмма LBP')
  axes[2].set_xlabel('Код LBP')
  axes[2].set_ylabel('Доля')
  axes[2].grid(True)

  plt.tight_layout()
  plt.show()

if __name__ == "__main__": 
  extract_lbp_features()
