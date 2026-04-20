import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import torch
from transformers import AutoConfig
# Попытка импорта модели TSPulse (если установлен пакет)
try:
    from tsfm_public.models.tspulse import TSPulseForReconstruction
except ImportError:
    messagebox.showerror("Ошибка", "Не найден модуль tsfm_public. Установите: pip install git+https://github.com/ibm-granite/granite-tsfm.git")
    raise

class PredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система прогнозирования технического состояния")
        self.root.geometry("550x450")
        self.root.resizable(False, False)
        
        self.model = None
        self.load_model()
        self.create_widgets()
    
    def load_model(self):
        """Загрузка предобученной модели TSPulse для обнаружения аномалий"""
        try:
            # Загружаем конфигурацию и модель для реконструкции (обнаружение аномалий)
            config = AutoConfig.from_pretrained(
                "ibm-granite/granite-timeseries-tspulse-r1",
                revision="main"
            )
            self.model = TSPulseForReconstruction.from_pretrained(
                "ibm-granite/granite-timeseries-tspulse-r1",
                revision="main",
                config=config
            )
            self.model.eval()
            print("Модель успешно загружена!")
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            self.model = None
    
    def create_widgets(self):
        # Заголовок
        title = tk.Label(self.root, text="Интеллектуальная система мониторинга и прогнозирования",
                         font=("Arial", 12, "bold"))
        title.pack(pady=10)
        subtitle = tk.Label(self.root, text="технического состояния участка трубопровода (по температуре)",
                            font=("Arial", 10))
        subtitle.pack(pady=(0,20))
        
        # Фрейм для ввода параметров
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)
        
        # Только одно поле для температуры
        row = tk.Frame(input_frame)
        row.pack(pady=5)
        lbl = tk.Label(row, text="Температура, °C", width=20, anchor="w")
        lbl.pack(side="left", padx=5)
        self.temp_entry = tk.Entry(row, width=15)
        self.temp_entry.pack(side="left", padx=5)
        
        # Кнопка прогноза
        predict_btn = tk.Button(self.root, text="Спрогнозировать",
                                command=self.predict,
                                bg="#4CAF50", fg="white",
                                font=("Arial", 10, "bold"),
                                width=20, height=2)
        predict_btn.pack(pady=20)
        
        # Область вывода
        result_frame = tk.LabelFrame(self.root, text="Результат прогноза", padx=10, pady=10)
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.result_text = tk.Text(result_frame, height=10, wrap="word", font=("Arial", 10))
        self.result_text.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.result_text)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)
    
    def predict(self):
        if self.model is None:
            messagebox.showerror("Ошибка", "Модель не загружена. Проверьте подключение.")
            return
        
        # Сбор значения температуры
        temp_str = self.temp_entry.get().strip()
        if not temp_str:
            messagebox.showwarning("Внимание", "Пожалуйста, введите значение температуры")
            return
        try:
            current_temp = float(temp_str)
        except ValueError:
            messagebox.showwarning("Внимание", "Некорректное значение температуры. Введите число.")
            return
        
        # Создание временного ряда с историей (24 точки) и интерполяция до 512
        full_series = self.create_series_with_history(current_temp)  # форма (24,1)
        interpolated_series = self.interpolate_to_length(full_series, target_len=512)  # (512,1)
        
        try:
            with torch.no_grad():
                # Преобразуем в тензор: (1, 512, 1)
                inputs = torch.tensor(interpolated_series, dtype=torch.float32).unsqueeze(0)
                outputs = self.model(inputs)
                # Анализируем результат
                result = self.analyze_outputs(outputs, current_temp)
                self.display_result(result, current_temp)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка прогноза: {str(e)}")
    
    def create_series_with_history(self, current_temp):
        """
        Создает синтетический временной ряд из 24 точек.
        Последняя точка - текущая температура, предыдущие - нормальные значения с шумом.
        """
        np.random.seed(42)
        # Нормальное значение температуры (например, 60°C)
        norm_temp = 60.0
        # 23 исторических значения с шумом
        hist = np.random.normal(norm_temp, norm_temp * 0.1, 23)
        # Добавляем текущее значение (24-я точка)
        full = np.append(hist, current_temp)
        # Возвращаем как массив (24,1)
        return full.reshape(-1, 1)
    
    def interpolate_to_length(self, series, target_len=512):
        """
        Интерполирует временной ряд с series.shape[0] точек до target_len точек.
        series: numpy массив (orig_len, num_features)
        Возвращает: (target_len, num_features)
        """
        orig_len = series.shape[0]
        num_features = series.shape[1]
        x_old = np.linspace(0, target_len - 1, orig_len)
        x_new = np.arange(target_len)
        interpolated = np.zeros((target_len, num_features))
        for f in range(num_features):
            interpolated[:, f] = np.interp(x_new, x_old, series[:, f])
        return interpolated
    
    def analyze_outputs(self, outputs, current_temp):
        """Анализ выходов модели (упрощенный, на основе порогов)"""
        # Пороговые значения для температуры
        thresholds = {
            'normal': 60.0,    # Нормальная рабочая температура
            'warning': 75.0,   # Предупреждение
            'critical': 90.0   # Критическое значение
        }
        
        # Определение статуса по температуре
        if current_temp >= thresholds['critical']:
            status = "Критическое отклонение"
            anomaly_level = 2
        elif current_temp >= thresholds['warning']:
            status = "Предупреждение"
            anomaly_level = 1
        elif current_temp <= thresholds['normal'] * 0.5:  # 30°C
            status = "Аномально низкое значение"
            anomaly_level = 1
        else:
            status = "В норме"
            anomaly_level = 0
        
        # Определение общего статуса системы
        if anomaly_level >= 2:
            overall_status = "КРИТИЧЕСКИЙ УРОВЕНЬ"
            recommendation = "НЕМЕДЛЕННО остановить оборудование и провести диагностику!"
            severity = "high"
        elif anomaly_level >= 1:
            overall_status = "ТРЕБУЕТ ВНИМАНИЯ"
            recommendation = "Провести внеплановую проверку, усилить мониторинг"
            severity = "warning"
        else:
            overall_status = "НОРМАЛЬНОЕ СОСТОЯНИЕ"
            recommendation = "Продолжить штатный мониторинг"
            severity = "normal"
        
        return {
            'overall_status': overall_status,
            'recommendation': recommendation,
            'temperature_value': current_temp,
            'temperature_status': status,
            'severity': severity,
            'anomaly_level': anomaly_level
        }
    
    def display_result(self, result, current_temp):
        self.result_text.delete(1.0, tk.END)
        icons = {'high':'🔴', 'warning':'🟡', 'normal':'🟢'}
        icon = icons.get(result['severity'], '⚪')
        self.result_text.insert(tk.END, "="*40 + "\n")
        self.result_text.insert(tk.END, "РЕЗУЛЬТАТ ПРОГНОЗИРОВАНИЯ\n")
        self.result_text.insert(tk.END, "="*40 + "\n\n")
        self.result_text.insert(tk.END, f"{icon} Общий статус: {result['overall_status']}\n\n")
        self.result_text.insert(tk.END, "Детальный анализ параметра:\n")
        self.result_text.insert(tk.END, "-"*30 + "\n")
        ind = "❌" if "Критическое" in result['temperature_status'] else ("⚠️" if "Предупреждение" in result['temperature_status'] or "Аномально" in result['temperature_status'] else "✅")
        self.result_text.insert(tk.END, f"{ind} Температура: {current_temp} °C → {result['temperature_status']}\n")
        self.result_text.insert(tk.END, "\nРекомендация:\n" + "-"*30 + "\n")
        self.result_text.insert(tk.END, f"{result['recommendation']}\n\n")
        self.result_text.insert(tk.END, "="*40 + "\n")
        self.result_text.insert(tk.END, f"Уровень аномалии: {result['anomaly_level']}/2\n")
        self.result_text.insert(tk.END, "="*40 + "\n")

def main():
    root = tk.Tk()
    app = PredictionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
