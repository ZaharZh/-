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
        subtitle = tk.Label(self.root, text="технического состояния участка трубопровода",
                            font=("Arial", 10))
        subtitle.pack(pady=(0,20))
        
        # Фрейм для ввода параметров
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)
        
        self.param_entries = {}
        param_names = [
            ("Вибрация, мм/с", "vibration"),
            ("Давление, МПа", "pressure"),
            ("Температура, °C", "temperature"),
            ("Расход нефти, м³/ч", "flow_rate")
        ]
        
        for label_text, param_key in param_names:
            row = tk.Frame(input_frame)
            row.pack(pady=5)
            lbl = tk.Label(row, text=label_text, width=20, anchor="w")
            lbl.pack(side="left", padx=5)
            ent = tk.Entry(row, width=15)
            ent.pack(side="left", padx=5)
            self.param_entries[param_key] = ent
        
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
        
        # Сбор значений
        current_values = []
        for key, entry in self.param_entries.items():
            val_str = entry.get().strip()
            if not val_str:
                messagebox.showwarning("Внимание", f"Заполните поле '{key}'")
                return
            try:
                current_values.append(float(val_str))
            except ValueError:
                messagebox.showwarning("Внимание", f"Некорректное число в поле '{key}'")
                return
        
        # Создание временного ряда с историей (24 точки) и интерполяция до 512
        full_series = self.create_series_with_history(current_values)  # форма (24,4)
        interpolated_series = self.interpolate_to_length(full_series, target_len=512)  # (512,4)
        
        try:
            with torch.no_grad():
                # Преобразуем в тензор: (1, 512, 4)
                inputs = torch.tensor(interpolated_series, dtype=torch.float32).unsqueeze(0)
                outputs = self.model(inputs)
                # Анализируем результат (здесь используем текущие значения для детального анализа)
                result = self.analyze_outputs(outputs, current_values)
                self.display_result(result, current_values)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка прогноза: {str(e)}")
    
    def create_series_with_history(self, current_values):
        """
        Создает синтетический временной ряд из 24 точек.
        Последняя точка - текущие показания, предыдущие - нормальные значения с шумом.
        """
        np.random.seed(42)
        param_ranges = {
            'vibration': {'norm': 2.0, 'threshold': 5.0},
            'pressure': {'norm': 5.0, 'threshold': 8.0},
            'temperature': {'norm': 60.0, 'threshold': 90.0},
            'flow_rate': {'norm': 1000.0, 'threshold': 1200.0}
        }
        param_names = ['vibration', 'pressure', 'temperature', 'flow_rate']
        series = []
        for i, pname in enumerate(param_names):
            norm_val = param_ranges[pname]['norm']
            # 23 исторических значения с шумом
            hist = np.random.normal(norm_val, norm_val * 0.1, 23)
            # Добавляем текущее значение (24-я точка)
            full = np.append(hist, current_values[i])
            series.append(full)
        # Транспонируем: (24,4)
        return np.array(series).T
    
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
    
    def analyze_outputs(self, outputs, current_values):
        """Анализ выходов модели (упрощенный, на основе порогов)"""
        param_names = ['Вибрация', 'Давление', 'Температура', 'Расход нефти']
        thresholds = {
            'Вибрация': {'normal': 2.0, 'warning': 3.5, 'critical': 5.0},
            'Давление': {'normal': 5.0, 'warning': 6.5, 'critical': 8.0},
            'Температура': {'normal': 60.0, 'warning': 75.0, 'critical': 90.0},
            'Расход нефти': {'normal': 1000.0, 'warning': 1100.0, 'critical': 1200.0}
        }
        param_status = []
        anomaly_count = 0
        for i, (pname, val) in enumerate(zip(param_names, current_values)):
            th = thresholds[pname]
            if val >= th['critical']:
                status = "Критическое отклонение"
                anomaly_count += 2
            elif val >= th['warning']:
                status = "Предупреждение"
                anomaly_count += 1
            elif val <= th['normal'] * 0.5:
                status = "Аномально низкое значение"
                anomaly_count += 1
            else:
                status = "В норме"
            param_status.append((pname, val, status))
        
        if anomaly_count >= 3:
            overall = "КРИТИЧЕСКИЙ УРОВЕНЬ"
            recommendation = "НЕМЕДЛЕННО остановить оборудование и провести диагностику!"
            severity = "high"
        elif anomaly_count >= 2:
            overall = "ТРЕБУЕТ ВНИМАНИЯ"
            recommendation = "Провести внеплановую проверку, усилить мониторинг"
            severity = "warning"
        elif anomaly_count >= 1:
            overall = "ПОТЕНЦИАЛЬНЫЙ РИСК"
            recommendation = "Планировать ремонт в ближайшее время"
            severity = "medium"
        else:
            overall = "НОРМАЛЬНОЕ СОСТОЯНИЕ"
            recommendation = "Продолжить штатный мониторинг"
            severity = "normal"
        
        return {
            'overall_status': overall,
            'recommendation': recommendation,
            'param_status': param_status,
            'severity': severity,
            'anomaly_count': anomaly_count
        }
    
    def display_result(self, result, current_values):
        self.result_text.delete(1.0, tk.END)
        icons = {'high':'🔴', 'warning':'🟡', 'medium':'🟠', 'normal':'🟢'}
        icon = icons.get(result['severity'], '⚪')
        self.result_text.insert(tk.END, "="*40 + "\n")
        self.result_text.insert(tk.END, "РЕЗУЛЬТАТ ПРОГНОЗИРОВАНИЯ\n")
        self.result_text.insert(tk.END, "="*40 + "\n\n")
        self.result_text.insert(tk.END, f"{icon} Общий статус: {result['overall_status']}\n\n")
        self.result_text.insert(tk.END, "Детальный анализ параметров:\n")
        self.result_text.insert(tk.END, "-"*30 + "\n")
        for pname, val, status in result['param_status']:
            ind = "❌" if "Критическое" in status else ("⚠️" if "Предупреждение" in status or "Аномально" in status else "✅")
            self.result_text.insert(tk.END, f"{ind} {pname}: {val} → {status}\n")
        self.result_text.insert(tk.END, "\nРекомендация:\n" + "-"*30 + "\n")
        self.result_text.insert(tk.END, f"{result['recommendation']}\n\n")
        self.result_text.insert(tk.END, "="*40 + "\n")
        self.result_text.insert(tk.END, f"Уровень аномалий: {result['anomaly_count']}/8\n")
        self.result_text.insert(tk.END, "="*40 + "\n")

def main():
    root = tk.Tk()
    app = PredictionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
