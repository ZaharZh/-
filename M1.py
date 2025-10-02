import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QLineEdit, QComboBox,
                             QFileDialog, QMessageBox, QGroupBox, QTextEdit)
from PyQt6.QtCore import Qt
import re

class FunctionPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Построитель графиков функций')
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Левая панель - управление
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, stretch=1)
        
        # Правая панель - график
        plot_panel = self.create_plot_panel()
        main_layout.addWidget(plot_panel, stretch=3)
        
        # Переменные для управления графиком
        self.scale_factor = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.current_function_type = "analytical"
        
    def create_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Выбор типа функции
        type_group = QGroupBox("Тип функции")
        type_layout = QVBoxLayout()
        
        self.function_type = QComboBox()
        self.function_type.addItems(["Аналитическая", "Табличная"])
        self.function_type.currentTextChanged.connect(self.on_function_type_changed)
        type_layout.addWidget(QLabel("Выберите тип функции:"))
        type_layout.addWidget(self.function_type)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Панель для аналитической функции
        self.analytical_group = QGroupBox("Аналитическая функция")
        analytical_layout = QVBoxLayout()
        
        analytical_layout.addWidget(QLabel("Введите функцию f(x):"))
        self.function_input = QLineEdit()
        self.function_input.setText("sin(x)")
        self.function_input.setPlaceholderText("Например: sin(x), x**2 + 2*x + 1")
        analytical_layout.addWidget(self.function_input)
        
        analytical_layout.addWidget(QLabel("Диапазон x (min max):"))
        range_layout = QHBoxLayout()
        self.x_min_input = QLineEdit()
        self.x_min_input.setText("-10")
        self.x_max_input = QLineEdit()
        self.x_max_input.setText("10")
        range_layout.addWidget(self.x_min_input)
        range_layout.addWidget(QLabel("до"))
        range_layout.addWidget(self.x_max_input)
        analytical_layout.addLayout(range_layout)
        
        self.analytical_group.setLayout(analytical_layout)
        layout.addWidget(self.analytical_group)
        
        # Панель для табличной функции
        self.tabular_group = QGroupBox("Табличная функция")
        tabular_layout = QVBoxLayout()
        
        self.load_file_button = QPushButton("Выбрать файл")
        self.load_file_button.clicked.connect(self.load_data_file)
        tabular_layout.addWidget(self.load_file_button)
        
        self.file_info = QLabel("Файл не выбран")
        tabular_layout.addWidget(self.file_info)
        
        self.data_preview = QTextEdit()
        self.data_preview.setMaximumHeight(150)
        self.data_preview.setReadOnly(True)
        tabular_layout.addWidget(QLabel("Предпросмотр данных:"))
        tabular_layout.addWidget(self.data_preview)
        
        self.tabular_group.setLayout(tabular_layout)
        layout.addWidget(self.tabular_group)
        self.tabular_group.hide()
        
        # Управление графиком
        control_group = QGroupBox("Управление графиком")
        control_layout = QVBoxLayout()
        
        # Масштабирование
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Масштаб:"))
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        scale_layout.addWidget(self.zoom_in_btn)
        scale_layout.addWidget(self.zoom_out_btn)
        control_layout.addLayout(scale_layout)
        
        # Смещение
        offset_layout = QHBoxLayout()
        offset_layout.addWidget(QLabel("Смещение:"))
        self.left_btn = QPushButton("←")
        self.left_btn.clicked.connect(lambda: self.move_graph(-1, 0))
        self.right_btn = QPushButton("→")
        self.right_btn.clicked.connect(lambda: self.move_graph(1, 0))
        self.up_btn = QPushButton("↑")
        self.up_btn.clicked.connect(lambda: self.move_graph(0, 1))
        self.down_btn = QPushButton("↓")
        self.down_btn.clicked.connect(lambda: self.move_graph(0, -1))
        offset_layout.addWidget(self.left_btn)
        offset_layout.addWidget(self.right_btn)
        offset_layout.addWidget(self.up_btn)
        offset_layout.addWidget(self.down_btn)
        control_layout.addLayout(offset_layout)
        
        # Сброс
        reset_btn = QPushButton("Сброс вида")
        reset_btn.clicked.connect(self.reset_view)
        control_layout.addWidget(reset_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Построение графика
        plot_btn = QPushButton("Построить график")
        plot_btn.clicked.connect(self.plot_function)
        layout.addWidget(plot_btn)
        
        # Информация
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Готов к работе")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        return panel
    
    def create_plot_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Создание Figure и Canvas для matplotlib
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Инициализация пустого графика
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.axhline(y=0, color='k', linewidth=1)
        self.ax.axvline(x=0, color='k', linewidth=1)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('f(x)')
        self.ax.set_title('График функции')
        self.canvas.draw()
        
        return panel
    
    def on_function_type_changed(self, text):
        if text == "Аналитическая":
            self.analytical_group.show()
            self.tabular_group.hide()
            self.current_function_type = "analytical"
        else:
            self.analytical_group.hide()
            self.tabular_group.show()
            self.current_function_type = "tabular"
    
    def load_data_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл с данными", "", "Text Files (*.txt);;All Files (*)")
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Парсинг данных
                self.table_data = self.parse_table_data(content)
                self.file_info.setText(f"Загружен: {file_path.split('/')[-1]}")
                
                # Показ предпросмотра
                preview_lines = content.split('\n')[:10]
                preview_text = '\n'.join(preview_lines)
                self.data_preview.setText(preview_text)
                
                self.info_label.setText(f"Загружено {len(self.table_data)} точек из файла")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def parse_table_data(self, content):
        """Парсинг табличных данных из текста"""
        data = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Разделение различными разделителями
            parts = re.split(r'[,\s;]+', line)
            if len(parts) >= 2:
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    data.append((x, y))
                except ValueError:
                    continue
        
        # Сортировка по x
        data.sort(key=lambda point: point[0])
        return data
    
    def parse_function(self, func_string):
        """Парсинг математической функции"""
        # Замена математических обозначений на синтаксис Python
        replacements = {
            'sin': 'np.sin',
            'cos': 'np.cos',
            'tan': 'np.tan',
            'exp': 'np.exp',
            'log': 'np.log',
            'log10': 'np.log10',
            'sqrt': 'np.sqrt',
            '^': '**'
        }
        
        for old, new in replacements.items():
            func_string = func_string.replace(old, new)
        
        return func_string
    
    def safe_eval_function(self, func_string, x):
        """Безопасное вычисление функции"""
        try:
            # Создаем безопасное пространство имен для eval
            safe_dict = {
                'x': x,
                'np': np,
                'sin': np.sin,
                'cos': np.cos,
                'tan': np.tan,
                'exp': np.exp,
                'log': np.log,
                'log10': np.log10,
                'sqrt': np.sqrt
            }
            
            # Удаляем потенциально опасные функции
            safe_dict['__builtins__'] = {}
            
            return eval(func_string, safe_dict)
        except:
            return np.nan
    
    def plot_function(self):
        try:
            self.ax.clear()
            
            if self.current_function_type == "analytical":
                self.plot_analytical_function()
            else:
                self.plot_tabular_function()
            
            # Настройка осей с учетом масштаба и смещения
            x_center = self.offset_x
            y_center = self.offset_y
            x_range = 10 / self.scale_factor
            y_range = 10 / self.scale_factor
            
            self.ax.set_xlim(x_center - x_range, x_center + x_range)
            self.ax.set_ylim(y_center - y_range, y_center + y_range)
            
            # Оси координат
            self.ax.axhline(y=0, color='k', linewidth=1)
            self.ax.axvline(x=0, color='k', linewidth=1)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('f(x)')
            self.ax.set_title('График функции')
            
            # Форматирование подписей осей для лучшего отображения при малых масштабах
            if self.scale_factor > 10:
                self.ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.4f'))
                self.ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.4f'))
            
            self.canvas.draw()
            self.info_label.setText("График построен успешно")
            
        except Exception as e:
            self.info_label.setText(f"Ошибка при построении графика: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось построить график: {str(e)}")
    
    def plot_analytical_function(self):
        func_string = self.function_input.text().strip()
        x_min = float(self.x_min_input.text())
        x_max = float(self.x_max_input.text())
        
        # Парсинг функции
        parsed_func = self.parse_function(func_string)
        
        # Генерация точек
        x = np.linspace(x_min, x_max, 1000)
        y = np.array([self.safe_eval_function(parsed_func, xi) for xi in x])
        
        # Отсеиваем NaN значения
        valid_mask = ~np.isnan(y)
        x_valid = x[valid_mask]
        y_valid = y[valid_mask]
        
        if len(x_valid) > 0:
            self.ax.plot(x_valid, y_valid, 'b-', linewidth=2, label=f'f(x) = {func_string}')
            self.ax.legend()
        else:
            raise ValueError("Не удалось вычислить функцию в заданном диапазоне")
    
    def plot_tabular_function(self):
        if not hasattr(self, 'table_data') or not self.table_data:
            raise ValueError("Нет загруженных табличных данных")
        
        x = [point[0] for point in self.table_data]
        y = [point[1] for point in self.table_data]
        
        self.ax.plot(x, y, 'ro-', linewidth=2, markersize=4, label='Табличная функция')
        self.ax.legend()
    
    def zoom_in(self):
        self.scale_factor *= 1.2
        self.plot_function()
    
    def zoom_out(self):
        self.scale_factor /= 1.2
        self.plot_function()
    
    def move_graph(self, dx, dy):
        move_step = 2.0 / self.scale_factor
        self.offset_x += dx * move_step
        self.offset_y += dy * move_step
        self.plot_function()
    
    def reset_view(self):
        self.scale_factor = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.plot_function()

def main():
    app = QApplication(sys.argv)
    
    # Установка стиля для лучшего внешнего вида
    app.setStyle('Fusion')
    
    plotter = FunctionPlotter()
    plotter.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
