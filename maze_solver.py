import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import time
import threading
from collections import deque
import json
import random

class MazeSolver:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[0 for _ in range(width)] for _ in range(height)]
        self.entrance = None
        self.exits = []
        self.all_routes = []
        self.shortest_routes = []
        
    def set_entrance(self, x, y):
        if self.is_valid_position(x, y) and self.maze[x][y] == 0:
            self.entrance = (x, y)
            return True
        return False
    
    def add_exit(self, x, y):
        if self.is_valid_position(x, y) and self.maze[x][y] == 0 and (x, y) != self.entrance:
            if (x, y) not in self.exits:
                self.exits.append((x, y))
                return True
        return False
    
    def remove_exit(self, x, y):
        if (x, y) in self.exits:
            self.exits.remove((x, y))
            return True
        return False
    
    def set_wall(self, x, y):
        if self.is_valid_position(x, y):
            self.maze[x][j] = 1
            return True
        return False
    
    def set_passage(self, x, y):
        if self.is_valid_position(x, y):
            self.maze[x][y] = 0
            return True
        return False
    
    def is_valid_position(self, x, y):
        return 0 <= x < self.height and 0 <= y < self.width
    
    def is_passage(self, x, y):
        return self.is_valid_position(x, y) and self.maze[x][y] == 0
    
    def get_neighbors(self, x, y):
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_passage(nx, ny):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def lee_algorithm(self, start, end):
        if not self.is_passage(start[0], start[1]) or not self.is_passage(end[0], end[1]):
            return None
        
        queue = deque([start])
        visited = {start: 0}
        parent = {start: None}
        
        while queue:
            current = queue.popleft()
            
            if current == end:
                path = []
                while current is not None:
                    path.append(current)
                    current = parent[current]
                return path[::-1]
            
            for neighbor in self.get_neighbors(current[0], current[1]):
                if neighbor not in visited:
                    visited[neighbor] = visited[current] + 1
                    parent[neighbor] = current
                    queue.append(neighbor)
        
        return None
    
    def find_all_routes(self):
        if not self.entrance or not self.exits:
            return []
        
        self.all_routes = []
        self.shortest_routes = []
        
        for exit_point in self.exits:
            route = self.lee_algorithm(self.entrance, exit_point)
            if route:
                self.all_routes.append({
                    'path': route,
                    'length': len(route) - 1,
                    'exit': exit_point
                })
        
        if self.all_routes:
            min_length = min(route['length'] for route in self.all_routes)
            self.shortest_routes = [route for route in self.all_routes if route['length'] == min_length]
        
        return self.all_routes
    
    def dfs_all_paths(self, start, end, max_paths=150, max_length=70):
        if not self.is_passage(start[0], start[1]) or not self.is_passage(end[0], end[1]):
            return []
        
        all_paths = []
        visited = set()
        
        def dfs(current, path):
            if len(all_paths) >= max_paths:
                return
            
            if len(path) > max_length:
                return
                
            if current == end:
                all_paths.append(path[:])
                return
            
            visited.add(current)
            
            for neighbor in self.get_neighbors(current[0], current[1]):
                if neighbor not in visited:
                    path.append(neighbor)
                    dfs(neighbor, path)
                    path.pop()
            
            visited.remove(current)
        
        dfs(start, [start])
        return all_paths
    
    def find_all_possible_routes(self):
        if not self.entrance or not self.exits:
            return []
        
        self.all_routes = []
        self.shortest_routes = []
        
        for exit_point in self.exits:
            routes = self.dfs_all_paths(self.entrance, exit_point)
            for route in routes:
                self.all_routes.append({
                    'path': route,
                    'length': len(route) - 1,
                    'exit': exit_point
                })
        
        if self.all_routes:
            min_length = min(route['length'] for route in self.all_routes)
            self.shortest_routes = [route for route in self.all_routes if route['length'] == min_length]
        
        return self.all_routes
    
    def generate_random_maze(self, wall_probability=0.3):
        self.maze = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for i in range(self.height):
            for j in range(self.width):
                if random.random() < wall_probability:
                    self.maze[i][j] = 1
        
        # Обеспечиваем проходимость по углам
        self.maze[0][0] = 0
        self.maze[0][self.width-1] = 0
        self.maze[self.height-1][0] = 0
        self.maze[self.height-1][self.width-1] = 0
        
        # Обеспечиваем проходимость в центре
        center_i, center_j = self.height // 2, self.width // 2
        for di in range(-1, 2):
            for dj in range(-1, 2):
                ni, nj = center_i + di, center_j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    self.maze[ni][nj] = 0
        
        self.entrance = None
        self.exits = []
        self.all_routes = []
        self.shortest_routes = []
    
    def clear_maze(self):
        self.maze = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.entrance = None
        self.exits = []
        self.all_routes = []
        self.shortest_routes = []
    
    def save_maze(self, filename):
        data = {
            'width': self.width,
            'height': self.height,
            'maze': self.maze,
            'entrance': self.entrance,
            'exits': self.exits
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
    
    def load_maze(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.width = data['width']
        self.height = data['height']
        self.maze = data['maze']
        self.entrance = tuple(data['entrance']) if data['entrance'] else None
        self.exits = [tuple(exit_point) for exit_point in data['exits']]
        self.all_routes = []
        self.shortest_routes = []

class ModernMazeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧭 Maze Pathfinder - Поиск путей в лабиринте")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f2f5')
        
        # Установка стиля
        self.setup_styles()
        
        self.maze_solver = None
        self.cell_size = 25
        self.current_route = 0
        self.animation_running = False
        self.animation_speed = 200
        
        self.edit_mode = "wall"
        self.drawing = False
        self.path_display_mode = "shortest"
        
        self.create_widgets()
        self.create_menu()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов
        self.colors = {
            'primary': '#4a6fa5',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#f0f2f5',
            'canvas_bg': '#ffffff'
        }
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый лабиринт", command=self.create_maze, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить", command=self.save_maze, accelerator="Ctrl+S")
        file_menu.add_command(label="Загрузить", command=self.load_maze, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Очистить лабиринт", command=self.clear_maze)
        edit_menu.add_command(label="Очистить пути", command=self.clear_paths)
        
        # Меню Поиск
        search_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Поиск", menu=search_menu)
        search_menu.add_command(label="Найти кратчайшие пути", command=self.find_shortest_paths, accelerator="F1")
        search_menu.add_command(label="Найти все пути", command=self.find_all_paths, accelerator="F2")
        
        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        
    def create_widgets(self):
        # Основной контейнер с сеткой
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель управления
        left_panel = ttk.Frame(main_container, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Правая панель с лабиринтом
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Создание левой панели
        self.create_left_panel(left_panel)
        
        # Создание правой панели
        self.create_right_panel(right_panel)
        
    def create_left_panel(self, parent):
        # Секция создания лабиринта
        create_frame = ttk.LabelFrame(parent, text="Создание лабиринта", padding=10)
        create_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Размеры
        size_frame = ttk.Frame(create_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="Ширина:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.width_var = tk.StringVar(value="25")
        width_spin = ttk.Spinbox(size_frame, from_=5, to=100, textvariable=self.width_var, width=10)
        width_spin.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(size_frame, text="Высота:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.height_var = tk.StringVar(value="25")
        height_spin = ttk.Spinbox(size_frame, from_=5, to=100, textvariable=self.height_var, width=10)
        height_spin.grid(row=0, column=3)
        
        ttk.Button(create_frame, text="Создать пустой лабиринт", 
                  command=self.create_maze, style="Primary.TButton").pack(fill=tk.X, pady=(0, 5))
        
        # Генерация случайного лабиринта
        gen_frame = ttk.Frame(create_frame)
        gen_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(gen_frame, text="Плотность стен: 30%").pack(anchor=tk.W)
        self.wall_density_var = tk.IntVar(value=30)
        density_scale = ttk.Scale(gen_frame, from_=10, to=70, variable=self.wall_density_var,
                                 command=lambda v: self.update_density_label())
        density_scale.pack(fill=tk.X, pady=(0, 5))
        
        self.density_label = ttk.Label(gen_frame, text="30%")
        self.density_label.pack(anchor=tk.E)
        
        ttk.Button(create_frame, text="Сгенерировать случайный лабиринт", 
                  command=self.generate_random, style="Success.TButton").pack(fill=tk.X)
        
        # Секция редактирования
        edit_frame = ttk.LabelFrame(parent, text="Режим редактирования", padding=10)
        edit_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.edit_mode_var = tk.StringVar(value="wall")
        
        # Кнопки режимов редактирования в сетке
        modes_frame = ttk.Frame(edit_frame)
        modes_frame.pack(fill=tk.X)
        
        modes = [
            ("🧱 Стена", "wall", "#dc3545"),
            ("🟩 Проход", "passage", "#28a745"),
            ("🚪 Вход", "entrance", "#4a6fa5"),
            ("🚪 Выход", "exit", "#ffc107")
        ]
        
        for i, (text, value, color) in enumerate(modes):
            btn = ttk.Radiobutton(modes_frame, text=text, variable=self.edit_mode_var, 
                                 value=value, command=self.change_edit_mode)
            btn.grid(row=i//2, column=i%2, sticky=tk.W+tk.E, padx=2, pady=2)
            btn.configure(style="Toolbutton.TRadiobutton")
        
        # Секция поиска путей
        search_frame = ttk.LabelFrame(parent, text="Поиск путей", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(search_frame, text="🔍 Найти кратчайшие пути (BFS)", 
                  command=self.find_shortest_paths, style="Primary.TButton").pack(fill=tk.X, pady=2)
        ttk.Button(search_frame, text="🧭 Найти все пути (DFS)", 
                  command=self.find_all_paths, style="Info.TButton").pack(fill=tk.X, pady=2)
        
        # Управление маршрутами
        route_frame = ttk.LabelFrame(parent, text="Управление маршрутами", padding=10)
        route_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки навигации
        nav_frame = ttk.Frame(route_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(nav_frame, text="⏮ Первый", command=self.first_route, 
                  style="Secondary.TButton", width=8).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(nav_frame, text="◀ Предыдущий", command=self.prev_route, 
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Следующий ▶", command=self.next_route, 
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Последний ⏭", command=self.last_route, 
                  style="Secondary.TButton", width=8).pack(side=tk.LEFT, padx=(2, 0))
        
        # Режимы отображения
        display_frame = ttk.Frame(route_frame)
        display_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(display_frame, text="Показать все пути", command=self.show_all_paths,
                  style="Light.TButton").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        ttk.Button(display_frame, text="Показать кратчайшие", command=self.show_shortest_paths,
                  style="Success.TButton").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Скорость анимации
        speed_frame = ttk.Frame(route_frame)
        speed_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(speed_frame, text="Скорость анимации:").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="200")
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var, 
                                  values=["50", "100", "200", "500", "1000"], width=8)
        speed_combo.pack(side=tk.RIGHT)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(parent, text="Информация", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_frame, height=8, width=30, bg=self.colors['light'],
                                font=("Consolas", 9), relief=tk.FLAT)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.insert("1.0", "Готов к работе\n\n")
        self.info_text.config(state=tk.DISABLED)
        
        # Статистика
        stats_frame = ttk.Frame(info_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="Путей не найдено", 
                                    font=("Arial", 9, "bold"), foreground=self.colors['dark'])
        self.stats_label.pack(anchor=tk.W)
        
    def create_right_panel(self, parent):
        # Верхняя панель с инструментами
        top_toolbar = ttk.Frame(parent)
        top_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(top_toolbar, text="💾 Сохранить лабиринт", 
                  command=self.save_maze, style="Light.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_toolbar, text="📂 Загрузить лабиринт", 
                  command=self.load_maze, style="Light.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(top_toolbar, text="🧹 Очистить все", 
                  command=self.clear_maze, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        
        # Масштаб
        scale_frame = ttk.Frame(top_toolbar)
        scale_frame.pack(side=tk.RIGHT)
        
        ttk.Label(scale_frame, text="Масштаб:").pack(side=tk.LEFT, padx=(0, 5))
        self.scale_var = tk.StringVar(value="25")
        scale_combo = ttk.Combobox(scale_frame, textvariable=self.scale_var, 
                                  values=["15", "20", "25", "30", "35"], width=6)
        scale_combo.pack(side=tk.LEFT)
        scale_combo.bind("<<ComboboxSelected>>", self.change_scale)
        
        # Холст для лабиринта
        canvas_container = ttk.Frame(parent)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем скроллбары
        canvas_frame = ttk.Frame(canvas_container)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar = ttk.Scrollbar(canvas_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(canvas_frame, bg=self.colors['canvas_bg'], 
                               yscrollcommand=v_scrollbar.set,
                               xscrollcommand=h_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # Легенда
        legend_frame = ttk.Frame(parent)
        legend_frame.pack(fill=tk.X, pady=(10, 0))
        
        legend_items = [
            ("🧱", "black", "Стена"),
            ("⬜", "white", "Проход"),
            ("🔵", "blue", "Вход"),
            ("🔴", "red", "Выход"),
            ("🟢", "green", "Кратчайший путь"),
            ("🟣", "purple", "Обычный путь")
        ]
        
        for symbol, color, desc in legend_items:
            item_frame = ttk.Frame(legend_frame)
            item_frame.pack(side=tk.LEFT, padx=10)
            ttk.Label(item_frame, text=symbol, font=("Arial", 12)).pack(side=tk.LEFT)
            ttk.Label(item_frame, text=desc, font=("Arial", 9)).pack(side=tk.LEFT, padx=(5, 0))
    
    def update_density_label(self):
        self.density_label.config(text=f"{self.wall_density_var.get()}%")
    
    def change_edit_mode(self):
        self.edit_mode = self.edit_mode_var.get()
    
    def change_scale(self, event=None):
        try:
            self.cell_size = int(self.scale_var.get())
            if self.maze_solver:
                self.draw_maze()
        except ValueError:
            pass
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_maze(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width < 5 or height < 5:
                raise ValueError("Размеры должны быть не менее 5x5")
            if width > 100 or height > 100:
                raise ValueError("Размеры не должны превышать 100x100")
            
            self.maze_solver = MazeSolver(width, height)
            self.current_route = 0
            self.animation_running = False
            
            # Устанавливаем вход и выход по умолчанию
            if width > 2 and height > 2:
                self.maze_solver.set_entrance(0, 0)
                self.maze_solver.add_exit(height-1, width-1)
            
            self.draw_maze()
            self.update_info("Новый лабиринт создан")
            self.update_stats()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def generate_random(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            wall_density = self.wall_density_var.get() / 100.0
            
            if width < 5 or height < 5:
                raise ValueError("Размеры должны быть не менее 5x5")
            
            self.maze_solver = MazeSolver(width, height)
            self.maze_solver.generate_random_maze(wall_density)
            
            # Устанавливаем вход и выход
            self.maze_solver.set_entrance(0, 0)
            self.maze_solver.add_exit(height-1, width-1)
            
            self.current_route = 0
            self.animation_running = False
            self.draw_maze()
            
            self.update_info(f"Случайный лабиринт создан\nРазмер: {width}x{height}\nПлотность стен: {int(wall_density*100)}%")
            self.update_stats()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def on_canvas_click(self, event):
        if self.maze_solver is None:
            return
        
        x, y = self.get_cell_coordinates(event.x, event.y)
        if x is not None and y is not None:
            self.drawing = True
            self.edit_cell(x, y)
    
    def on_canvas_drag(self, event):
        if self.drawing and self.maze_solver is not None:
            x, y = self.get_cell_coordinates(event.x, event.y)
            if x is not None and y is not None:
                self.edit_cell(x, y)
    
    def on_canvas_release(self, event):
        self.drawing = False
    
    def get_cell_coordinates(self, canvas_x, canvas_y):
        if self.maze_solver is None:
            return None, None
        
        # Учитываем смещение скролла
        canvas_x = self.canvas.canvasx(canvas_x)
        canvas_y = self.canvas.canvasy(canvas_y)
        
        cell_x = int(canvas_y // self.cell_size)
        cell_y = int(canvas_x // self.cell_size)
        
        if 0 <= cell_x < self.maze_solver.height and 0 <= cell_y < self.maze_solver.width:
            return cell_x, cell_y
        return None, None
    
    def edit_cell(self, x, y):
        if self.maze_solver is None:
            return
        
        if self.edit_mode == "wall":
            self.maze_solver.set_wall(x, y)
        elif self.edit_mode == "passage":
            self.maze_solver.set_passage(x, y)
        elif self.edit_mode == "entrance":
            if self.maze_solver.is_passage(x, y):
                self.maze_solver.entrance = (x, y)
        elif self.edit_mode == "exit":
            if self.maze_solver.is_passage(x, y) and (x, y) != self.maze_solver.entrance:
                self.maze_solver.add_exit(x, y)
        
        self.draw_maze()
        self.update_stats()
    
    def draw_maze(self):
        if self.maze_solver is None:
            return
        
        self.canvas.delete("all")
        
        width = self.maze_solver.width
        height = self.maze_solver.height
        
        # Рассчитываем размеры холста
        canvas_width = width * self.cell_size
        canvas_height = height * self.cell_size
        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # Рисуем сетку
        for i in range(height):
            for j in range(width):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Рисуем клетку
                if self.maze_solver.maze[i][j] == 1:
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                fill="#495057", 
                                                outline="#6c757d",
                                                width=1)
                    # Текстура стены
                    self.canvas.create_line(x1+2, y1+2, x2-2, y2-2, 
                                           fill="#343a40", width=1)
                    self.canvas.create_line(x2-2, y1+2, x1+2, y2-2, 
                                           fill="#343a40", width=1)
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                fill="#e9ecef", 
                                                outline="#dee2e6",
                                                width=1)
        
        # Рисуем вход
        if self.maze_solver.entrance:
            x, y = self.maze_solver.entrance
            x1 = y * self.cell_size
            y1 = x * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            
            # Градиент для входа
            for i in range(self.cell_size):
                color_val = 255 - int(i * 100 / self.cell_size)
                color = f'#{color_val:02x}{color_val:02x}255'
                self.canvas.create_line(x1, y1+i, x2, y1+i, fill=color)
            
            self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, 
                                   text="🚪", font=("Arial", self.cell_size//2))
        
        # Рисуем выходы
        for exit_point in self.maze_solver.exits:
            x, y = exit_point
            x1 = y * self.cell_size
            y1 = x * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            
            # Градиент для выхода
            for i in range(self.cell_size):
                color_val = 255 - int(i * 100 / self.cell_size)
                color = f'#255{color_val:02x}{color_val:02x}'
                self.canvas.create_line(x1, y1+i, x2, y1+i, fill=color)
            
            self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, 
                                   text="🏁", font=("Arial", self.cell_size//2))
        
        # Обновляем скроллрегион
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def find_shortest_paths(self):
        if self.maze_solver is None:
            messagebox.showwarning("Предупреждение", "Сначала создайте лабиринт!")
            return
        
        if not self.maze_solver.entrance:
            messagebox.showwarning("Предупреждение", "Установите точку входа!")
            return
        
        if not self.maze_solver.exits:
            messagebox.showwarning("Предупреждение", "Установите хотя бы одну точку выхода!")
            return
        
        self.update_info("Поиск кратчайших путей (алгоритм Ли)...")
        
        # Запускаем в отдельном потоке, чтобы не блокировать GUI
        threading.Thread(target=self._find_shortest_paths_thread, daemon=True).start()
    
    def _find_shortest_paths_thread(self):
        routes = self.maze_solver.find_all_routes()
        
        if routes:
            self.current_route = 0
            self.path_display_mode = "shortest"
            shortest_length = routes[0]['length'] if routes else 0
            
            self.root.after(0, self.update_info, 
                          f"Найдено кратчайших путей: {len(routes)}\n"
                          f"Длина кратчайшего пути: {shortest_length}\n"
                          f"Вход: {self.maze_solver.entrance}\n"
                          f"Выходы: {len(self.maze_solver.exits)}")
            
            self.root.after(0, self.update_stats)
            self.root.after(0, self.draw_routes)
        else:
            self.root.after(0, self.update_info, "Пути не найдены")
            self.root.after(0, messagebox.showinfo, "Результат", "Пути от входа до выходов не найдены")
    
    def find_all_paths(self):
        if self.maze_solver is None:
            messagebox.showwarning("Предупреждение", "Сначала создайте лабиринт!")
            return
        
        if not self.maze_solver.entrance:
            messagebox.showwarning("Предупреждение", "Установите точку входа!")
            return
        
        if not self.maze_solver.exits:
            messagebox.showwarning("Предупреждение", "Установите хотя бы одну точку выхода!")
            return
        
        maze_size = self.maze_solver.width * self.maze_solver.height
        if maze_size > 400:
            result = messagebox.askyesno("Предупреждение", 
                                       f"Лабиринт большой ({self.maze_solver.width}x{self.maze_solver.height}).\n"
                                       f"Поиск всех путей может занять много времени.\n"
                                       f"Продолжить?")
            if not result:
                return
        
        self.update_info("Поиск всех возможных путей (DFS)...")
        
        threading.Thread(target=self._find_all_paths_thread, daemon=True).start()
    
    def _find_all_paths_thread(self):
        try:
            routes = self.maze_solver.find_all_possible_routes()
            
            if routes:
                self.current_route = 0
                self.path_display_mode = "all"
                shortest_length = self.maze_solver.shortest_routes[0]['length'] if self.maze_solver.shortest_routes else 0
                
                self.root.after(0, self.update_info,
                              f"Найдено путей: {len(routes)}\n"
                              f"Кратчайших: {len(self.maze_solver.shortest_routes)}\n"
                              f"Длина кратчайшего: {shortest_length}\n"
                              f"Ограничение: 150 путей")
                
                self.root.after(0, self.update_stats)
                self.root.after(0, self.draw_routes)
            else:
                self.root.after(0, self.update_info, "Пути не найдены")
                self.root.after(0, messagebox.showinfo, "Результат", "Пути от входа до выходов не найдены")
        except Exception as e:
            self.root.after(0, self.update_info, f"Ошибка при поиске путей: {e}")
            self.root.after(0, messagebox.showerror, "Ошибка", f"Произошла ошибка при поиске путей: {e}")
    
    def draw_routes(self):
        if not self.maze_solver.all_routes:
            return
        
        self.draw_maze()
        
        routes_to_show = self.maze_solver.shortest_routes if self.path_display_mode == "shortest" else self.maze_solver.all_routes
        
        # Цвета для разных типов путей
        shortest_colors = ["#28a745", "#218838", "#1e7e34"]
        normal_colors = [
            "#dc3545", "#007bff", "#6f42c1", "#fd7e14", "#17a2b8",
            "#e83e8c", "#20c997", "#ffc107", "#6c757d", "#343a40"
        ]
        
        for i, route in enumerate(routes_to_show):
            if self.path_display_mode == "shortest":
                color = shortest_colors[i % len(shortest_colors)]
                width = 3
            else:
                if route in self.maze_solver.shortest_routes:
                    color = shortest_colors[0]
                    width = 3
                else:
                    color = normal_colors[i % len(normal_colors)]
                    width = 2
            
            # Рисуем путь
            for j in range(len(route['path']) - 1):
                x1, y1 = route['path'][j]
                x2, y2 = route['path'][j + 1]
                
                canvas_x1 = y1 * self.cell_size + self.cell_size // 2
                canvas_y1 = x1 * self.cell_size + self.cell_size // 2
                canvas_x2 = y2 * self.cell_size + self.cell_size // 2
                canvas_y2 = x2 * self.cell_size + self.cell_size // 2
                
                self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                                       fill=color, width=width, capstyle=tk.ROUND, 
                                       arrow=tk.LAST if j == len(route['path']) - 2 else None)
            
            # Отмечаем начало и конец пути
            if route['path']:
                start_x, start_y = route['path'][0]
                end_x, end_y = route['path'][-1]
                
                # Начало пути
                canvas_x = start_y * self.cell_size + self.cell_size // 2
                canvas_y = start_x * self.cell_size + self.cell_size // 2
                self.canvas.create_oval(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5,
                                       fill=color, outline="white", width=2)
                
                # Конец пути
                canvas_x = end_y * self.cell_size + self.cell_size // 2
                canvas_y = end_x * self.cell_size + self.cell_size // 2
                self.canvas.create_rectangle(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5,
                                           fill=color, outline="white", width=2)
    
    def first_route(self):
        if self.maze_solver and self.maze_solver.all_routes:
            self.current_route = 0
            self.draw_single_route()
    
    def last_route(self):
        if self.maze_solver and self.maze_solver.all_routes:
            self.current_route = len(self.maze_solver.all_routes) - 1
            self.draw_single_route()
    
    def prev_route(self):
        if self.maze_solver and self.maze_solver.all_routes:
            self.current_route = (self.current_route - 1) % len(self.maze_solver.all_routes)
            self.draw_single_route()
    
    def next_route(self):
        if self.maze_solver and self.maze_solver.all_routes:
            self.current_route = (self.current_route + 1) % len(self.maze_solver.all_routes)
            self.draw_single_route()
    
    def draw_single_route(self):
        if not self.maze_solver or not self.maze_solver.all_routes:
            return
        
        self.draw_maze()
        
        route = self.maze_solver.all_routes[self.current_route]
        
        # Определяем цвет маршрута
        if route in self.maze_solver.shortest_routes:
            color = "#28a745"
            width = 3
        else:
            colors = ["#007bff", "#6f42c1", "#fd7e14", "#17a2b8", "#e83e8c"]
            color = colors[self.current_route % len(colors)]
            width = 2
        
        # Рисуем путь
        for j in range(len(route['path']) - 1):
            x1, y1 = route['path'][j]
            x2, y2 = route['path'][j + 1]
            
            canvas_x1 = y1 * self.cell_size + self.cell_size // 2
            canvas_y1 = x1 * self.cell_size + self.cell_size // 2
            canvas_x2 = y2 * self.cell_size + self.cell_size // 2
            canvas_y2 = x2 * self.cell_size + self.cell_size // 2
            
            self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                                   fill=color, width=width, capstyle=tk.ROUND,
                                   arrow=tk.LAST if j == len(route['path']) - 2 else None)
        
        self.update_info(f"Маршрут {self.current_route + 1}/{len(self.maze_solver.all_routes)}\n"
                        f"Длина: {route['length']} шагов\n"
                        f"Выход: {route['exit']}\n"
                        f"Тип: {'Кратчайший' if route in self.maze_solver.shortest_routes else 'Обычный'}")
    
    def show_all_paths(self):
        if self.maze_solver and self.maze_solver.all_routes:
            self.path_display_mode = "all"
            self.draw_routes()
            self.update_info(f"Показаны все пути: {len(self.maze_solver.all_routes)}\n"
                           f"Кратчайших: {len(self.maze_solver.shortest_routes)}")
    
    def show_shortest_paths(self):
        if self.maze_solver and self.maze_solver.shortest_routes:
            self.path_display_mode = "shortest"
            self.draw_routes()
            self.update_info(f"Показаны кратчайшие пути: {len(self.maze_solver.shortest_routes)}\n"
                           f"Длина: {self.maze_solver.shortest_routes[0]['length'] if self.maze_solver.shortest_routes else 0}")
    
    def clear_paths(self):
        if self.maze_solver:
            self.maze_solver.all_routes = []
            self.maze_solver.shortest_routes = []
            self.current_route = 0
            self.draw_maze()
            self.update_info("Все пути очищены")
            self.update_stats()
    
    def clear_maze(self):
        if self.maze_solver:
            self.maze_solver.clear_maze()
            self.current_route = 0
            self.animation_running = False
            self.draw_maze()
            self.update_info("Лабиринт очищен")
            self.update_stats()
    
    def save_maze(self):
        if self.maze_solver is None:
            messagebox.showwarning("Предупреждение", "Нет лабиринта для сохранения!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Все файлы", "*.*")],
            initialfile="maze.json"
        )
        
        if filename:
            try:
                self.maze_solver.save_maze(filename)
                self.update_info(f"Лабиринт сохранен в:\n{filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_maze(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("Все файлы", "*.*")]
        )
        
        if filename:
            try:
                self.maze_solver = MazeSolver(1, 1)
                self.maze_solver.load_maze(filename)
                self.current_route = 0
                self.animation_running = False
                self.draw_maze()
                self.update_info(f"Лабиринт загружен из:\n{filename}")
                self.update_stats()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")
    
    def update_info(self, message):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", f"{message}\n\n")
        self.info_text.config(state=tk.DISABLED)
    
    def update_stats(self):
        if self.maze_solver:
            stats = []
            stats.append(f"Размер: {self.maze_solver.width}×{self.maze_solver.height}")
            stats.append(f"Вход: {self.maze_solver.entrance if self.maze_solver.entrance else 'не установлен'}")
            stats.append(f"Выходов: {len(self.maze_solver.exits)}")
            
            if self.maze_solver.all_routes:
                stats.append(f"Найдено путей: {len(self.maze_solver.all_routes)}")
                if self.maze_solver.shortest_routes:
                    stats.append(f"Кратчайших: {len(self.maze_solver.shortest_routes)}")
                    stats.append(f"Длина: {self.maze_solver.shortest_routes[0]['length']}")
            
            self.stats_label.config(text=" | ".join(stats))
        else:
            self.stats_label.config(text="Лабиринт не создан")
    
    def show_about(self):
        about_text = """Maze Pathfinder v2.0

Приложение для поиска путей в лабиринте.

Функции:
• Создание и редактирование лабиринтов
• Поиск кратчайших путей (алгоритм Ли/BFS)
• Поиск всех возможных путей (DFS)
• Визуализация маршрутов
• Сохранение и загрузка лабиринтов

Управление:
ЛКМ - установка элемента
ПКМ - удаление элемента
Колесо мыши - прокрутка

Автор: Maze Pathfinder Team
Версия: 2.0"""
        
        messagebox.showinfo("О программе", about_text)

def main():
    root = tk.Tk()
    
    # Настройка стилей
    style = ttk.Style()
    
    # Создание стилей для кнопок
    style.configure("Primary.TButton", 
                   background="#4a6fa5", 
                   foreground="white",
                   padding=6,
                   font=("Arial", 10, "bold"))
    
    style.configure("Success.TButton", 
                   background="#28a745", 
                   foreground="white",
                   padding=6)
    
    style.configure("Danger.TButton", 
                   background="#dc3545", 
                   foreground="white",
                   padding=6)
    
    style.configure("Info.TButton", 
                   background="#17a2b8", 
                   foreground="white",
                   padding=6)
    
    style.configure("Light.TButton", 
                   background="#f8f9fa", 
                   foreground="#212529",
                   padding=6)
    
    style.configure("Secondary.TButton", 
                   background="#6c757d", 
                   foreground="white",
                   padding=6)
    
    style.configure("Toolbutton.TRadiobutton",
                   padding=8,
                   relief="flat")
    
    app = ModernMazeGUI(root)
    
    # Установка иконки (если есть)
    try:
        root.iconbitmap('maze_icon.ico')
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
