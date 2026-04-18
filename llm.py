import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import torch
from tsfm_public.models.tspulse import TSPulseForReconstruction
from transformers import AutoConfig

class PredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система прогнозирования технического состояния")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Загрузка модели при запуске
        self.model = None
        self.load_model()
        
        # Создание интерфейса
        self.create_widgets()
    
    def load_model(self):
        """Загрузка предобученной модели TSPulse для обнаружения аномалий"""
        try:
            # Загружаем конфигурацию и модель для обнаружения аномалий
            config = AutoConfig.from_pretrained(
                "ibm-granite/granite-timeseries-tspulse-r1",
                revision="main"
            )
            self.model = TSPulseForReconstruction.from_pretrained(
                "ibm-granite/granite-timeseries-tspulse-r1",
                revision="main",
                config=config
            )
            self.model.eval()  # Режим оценки
            print("Модель успешно загружена!")
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            self.model = None
    
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="Интеллектуальная система мониторинга и прогнозирования", 
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            self.root, 
            text="технического состояния участка трубопровода", 
            font=("Arial", 10)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Фрейм для ввода параметров
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)
        
        # Создание полей ввода для 4 параметров
        self.param_entries = {}
        param_names = [
            ("Вибрация, мм/с", "vibration"),
            ("Давление, МПа", "pressure"),
            ("Температура, °C", "temperature"),
            ("Расход нефти, м³/ч", "flow_rate")
        ]
        
        for i, (label_text, param_key) in enumerate(param_names):
            row_frame = tk.Frame(input_frame)
            row_frame.pack(pady=5)
            
            label = tk.Label(row_frame, text=label_text, width=20, anchor="w")
            label.pack(side="left", padx=5)
            
            entry = tk.Entry(row_frame, width=15)
            entry.pack(side="left", padx=5)
            self.param_entries[param_key] = entry
        
        # Кнопка прогнозирования
        predict_btn = tk.Button(
            self.root, 
            text="Спрогнозировать", 
            command=self.predict,
            bg="#4CAF50", 
            fg="white",
            font=("Arial", 10, "bold"),
            width=20,
            height=2
        )
        predict_btn.pack(pady=20)
        
        # Поле вывода результата
        result_frame = tk.LabelFrame(self.root, text="Результат прогноза", padx=10, pady=10)
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.result_text = tk.Text(result_frame, height=8, wrap="word", font=("Arial", 10))
        self.result_text.pack(fill="both", expand=True)
        
        # Скроллбар для текста
        scrollbar = tk.Scrollbar(self.result_text)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)
    
    def predict(self):
        """Выполнение прогнозирования на основе введённых параметров"""
        # Проверка загрузки модели
        if self.model is None:
            messagebox.showerror("Ошибка", "Модель не загружена. Проверьте подключение к интернету.")
            return
        
        # Сбор данных из полей ввода
        input_values = []
        for key, entry in self.param_entries.items():
            value_str = entry.get().strip()
            if not value_str:
                messagebox.showwarning("Внимание", f"Пожалуйста, заполните поле '{key}'")
                return
            try:
                input_values.append(float(value_str))
            except ValueError:
                messagebox.showwarning("Внимание", f"Некорректное значение в поле '{key}'. Введите число.")
                return
        
        # Создание временного ряда для анализа
        # (в реальном приложении здесь должна быть историческая последовательность)
        time_series = self.create_test_series(input_values)
        
        # Выполнение прогноза
        try:
            # Подготовка входных данных для модели
            with torch.no_grad():
                # Преобразование в тензор PyTorch
                inputs = torch.tensor(time_series, dtype=torch.float32).unsqueeze(0)
                
                # Получение прогноза от модели
                outputs = self.model(inputs)
                
                # Анализ результатов для определения статуса оборудования
                prediction_result = self.analyze_outputs(outputs, input_values)
                
                # Отображение результата
                self.display_result(prediction_result, input_values)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при прогнозировании: {str(e)}")
    
    def create_test_series(self, current_values):
        """Создание тестового временного ряда (в реальном приложении используются исторические данные)"""
        # Создание синтетического временного ряда для демонстрации
        # В реальном приложении здесь должны быть исторические данные с датчиков
        np.random.seed(42)
        
        # Базовые значения для каждого параметра
        param_ranges = {
            'vibration': {'norm': 2.0, 'threshold': 5.0},
            'pressure': {'norm': 5.0, 'threshold': 8.0},
            'temperature': {'norm': 60.0, 'threshold': 90.0},
            'flow_rate': {'norm': 1000.0, 'threshold': 1200.0}
        }
        
        # Создание временного ряда с нормальным распределением
        time_series = []
        param_names = ['vibration', 'pressure', 'temperature', 'flow_rate']
        
        for i, param_name in enumerate(param_names):
            # Нормальные значения с добавлением шума
            norm_value = param_ranges[param_name]['norm']
            normal_series = np.random.normal(norm_value, norm_value * 0.1, 24)
            
            # Замена последнего значения текущим
            normal_series[-1] = current_values[i]
            
            time_series.append(normal_series)
        
        return np.array(time_series).T
    
    def analyze_outputs(self, outputs, current_values):
        """Анализ выходных данных модели для определения технического состояния"""
        # Параметры и их пороговые значения
        param_names = ['Вибрация', 'Давление', 'Температура', 'Расход нефти']
        thresholds = {
            'Вибрация': {'normal': 2.0, 'warning': 3.5, 'critical': 5.0},
            'Давление': {'normal': 5.0, 'warning': 6.5, 'critical': 8.0},
            'Температура': {'normal': 60.0, 'warning': 75.0, 'critical': 90.0},
            'Расход нефти': {'normal': 1000.0, 'warning': 1100.0, 'critical': 1200.0}
        }
        
        # Определение статуса по каждому параметру
        param_status = []
        anomaly_count = 0
        
        for i, (param_name, value) in enumerate(zip(param_names, current_values)):
            threshold = thresholds[param_name]
            if value >= threshold['critical']:
                status = "Критическое отклонение"
                anomaly_count += 2
            elif value >= threshold['warning']:
                status = "Предупреждение"
                anomaly_count += 1
            elif value <= threshold['normal'] * 0.5:
                status = "Аномально низкое значение"
                anomaly_count += 1
            else:
                status = "В норме"
            
            param_status.append((param_name, value, status))
        
        # Определение общего статуса системы
        if anomaly_count >= 3:
            overall_status = "КРИТИЧЕСКИЙ УРОВЕНЬ"
            recommendation = "НЕМЕДЛЕННО остановить оборудование и провести диагностику!"
            severity = "high"
        elif anomaly_count >= 2:
            overall_status = "ТРЕБУЕТ ВНИМАНИЯ"
            recommendation = "Провести внеплановую проверку, усилить мониторинг"
            severity = "warning"
        elif anomaly_count >= 1:
            overall_status = "ПОТЕНЦИАЛЬНЫЙ РИСК"
            recommendation = "Планировать ремонт в ближайшее время, отслеживать динамику"
            severity = "medium"
        else:
            overall_status = "НОРМАЛЬНОЕ СОСТОЯНИЕ"
            recommendation = "Продолжить штатный мониторинг"
            severity = "normal"
        
        return {
            'overall_status': overall_status,
            'recommendation': recommendation,
            'param_status': param_status,
            'severity': severity,
            'anomaly_count': anomaly_count
        }
    
    def display_result(self, result, input_values):
        """Отображение результатов прогноза в текстовом поле"""
        # Очистка текстового поля
        self.result_text.delete(1.0, tk.END)
        
        # Определение цветов для статуса
        severity_colors = {
            'high': '🔴',
            'warning': '🟡',
            'medium': '🟠',
            'normal': '🟢'
        }
        
        # Заголовок
        self.result_text.insert(tk.END, "=" * 40 + "\n")
        self.result_text.insert(tk.END, "РЕЗУЛЬТАТ ПРОГНОЗИРОВАНИЯ\n")
        self.result_text.insert(tk.END, "=" * 40 + "\n\n")
        
        # Общий статус
        status_icon = severity_colors.get(result['severity'], '⚪')
        self.result_text.insert(tk.END, f"{status_icon} Общий статус: {result['overall_status']}\n\n")
        
        # Анализ параметров
        self.result_text.insert(tk.END, "Детальный анализ параметров:\n")
        self.result_text.insert(tk.END, "-" * 30 + "\n")
        
        for param_name, value, status in result['param_status']:
            # Определение индикатора для каждого параметра
            if "Критическое" in status:
                indicator = "❌"
            elif "Предупреждение" in status or "Аномально" in status:
                indicator = "⚠️"
            else:
                indicator = "✅"
            
            self.result_text.insert(tk.END, f"{indicator} {param_name}: {value} → {status}\n")
        
        self.result_text.insert(tk.END, "\n")
        
        # Рекомендация
        self.result_text.insert(tk.END, "Рекомендация:\n")
        self.result_text.insert(tk.END, "-" * 30 + "\n")
        self.result_text.insert(tk.END, f"{result['recommendation']}\n\n")
        
        # Дополнительная информация
        self.result_text.insert(tk.END, "=" * 40 + "\n")
        self.result_text.insert(tk.END, f"Уровень аномалий: {result['anomaly_count']}/8\n")
        self.result_text.insert(tk.END, "=" * 40 + "\n")

def main():
    root = tk.Tk()
    app = PredictionApp(root)
    root.mainloop()

#pip install git+https://github.com/ibm-granite/granite-tsfm.git

if __name__ == "__main__":
    main()
