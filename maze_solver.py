import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import time
import threading
from collections import deque
import json
import random
# Извлекается текущая вершина из очереди
# Если достигнута конечная точка - восстанавливается путь
# Иначе проверяются все соседние непосещенные клетки
# Соседи добавляются в очередь с пометкой о Родителей
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
            self.maze[x][y] = 1
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
    
    def generate_random_maze(self, wall_probability=0.3):
        self.maze = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for i in range(self.height):
            for j in range(self.width):
                if random.random() < wall_probability:
                    self.maze[i][j] = 1
        
        self.maze[0][0] = 0
        self.maze[0][self.width-1] = 0
        self.maze[self.height-1][0] = 0
        self.maze[self.height-1][self.width-1] = 0
        
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

class MazeGUI:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Лабиринт - поиск кратчайшего пути")
        self.root.geometry("1000x700")
        
        self.maze_solver = None
        self.cell_size = 20
        self.current_route = 0
        self.animation_running = False
        self.animation_speed = 200
        
        self.edit_mode = "wall"
        self.drawing = False
        self.path_display_mode = "shortest"
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = tk.LabelFrame(main_frame, text="Управление", padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        size_frame = tk.LabelFrame(control_frame, text="Размеры лабиринта", padx=5, pady=5)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(size_frame, text="Ширина:").pack(anchor=tk.W)
        self.width_var = tk.StringVar(value="20")
        tk.Entry(size_frame, textvariable=self.width_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        tk.Label(size_frame, text="Высота:").pack(anchor=tk.W)
        self.height_var = tk.StringVar(value="20")
        tk.Entry(size_frame, textvariable=self.height_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        tk.Button(size_frame, text="Создать лабиринт", command=self.create_maze,
                 bg="lightblue").pack(fill=tk.X, pady=2)
        
        gen_frame = tk.Frame(size_frame)
        gen_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(gen_frame, text="Плотность стен:").pack(anchor=tk.W)
        self.wall_density_var = tk.StringVar(value="30")
        density_scale = tk.Scale(gen_frame, from_=10, to=70, orient=tk.HORIZONTAL, 
                                variable=self.wall_density_var, length=150)
        density_scale.pack(anchor=tk.W)
        
        tk.Button(gen_frame, text="Сгенерировать случайно", command=self.generate_random,
                 bg="lightgreen").pack(fill=tk.X, pady=2)
        
        edit_frame = tk.LabelFrame(control_frame, text="Режимы редактирования", padx=5, pady=5)
        edit_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.edit_mode_var = tk.StringVar(value="wall")
        modes = [
            ("Стена", "wall"),
            ("Проход", "passage"),
            ("Вход", "entrance"),
            ("Выход", "exit")
        ]
        
        for text, value in modes:
            tk.Radiobutton(edit_frame, text=text, variable=self.edit_mode_var, 
                          value=value, command=self.change_edit_mode).pack(anchor=tk.W)
        
        button_frame = tk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="Найти кратчайший", command=self.find_shortest_paths,
                 bg="lightgreen").pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Найти все пути (до 100)", command=self.find_all_paths,
                 bg="lightblue").pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Очистить", command=self.clear_maze,
                 bg="lightcoral").pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Сохранить", command=self.save_maze,
                 bg="lightyellow").pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Загрузить", command=self.load_maze,
                 bg="lightcyan").pack(fill=tk.X, pady=2)
        
        route_frame = tk.LabelFrame(control_frame, text="Управление маршрутами", padx=5, pady=5)
        route_frame.pack(fill=tk.X, pady=(10, 0))
        
        route_control_frame = tk.Frame(route_frame)
        route_control_frame.pack(fill=tk.X)
        
        tk.Button(route_control_frame, text="◀", command=self.prev_route,
                 bg="orange", width=3).pack(side=tk.LEFT, padx=(0, 2))
        tk.Button(route_control_frame, text="▶", command=self.next_route,
                 bg="orange", width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(route_control_frame, text="⏹", command=self.stop_animation,
                 bg="lightcoral", width=3).pack(side=tk.LEFT, padx=(2, 0))
        
        display_mode_frame = tk.Frame(route_frame)
        display_mode_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(display_mode_frame, text="Все пути", command=self.show_all_paths,
                 bg="lightblue", width=8).pack(side=tk.LEFT, padx=(0, 2))
        tk.Button(display_mode_frame, text="Кратчайшие", command=self.show_shortest_paths,
                 bg="lightgreen", width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Label(route_frame, text="Скорость анимации (мс):").pack(anchor=tk.W)
        self.speed_var = tk.StringVar(value="200")
        tk.Entry(route_frame, textvariable=self.speed_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        info_frame = tk.LabelFrame(control_frame, text="Информация", padx=5, pady=5)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_label = tk.Label(info_frame, text="Готов к работе", wraplength=150)
        self.info_label.pack()
        
        self.shortest_length_label = tk.Label(info_frame, text="Длина кратчайшего: -", 
                                             font=("Arial", 9, "bold"), fg="darkgreen", 
                                             bg="lightyellow", relief="raised", bd=1)
        self.shortest_length_label.pack(pady=(5, 0))
        
        
        canvas_frame = tk.LabelFrame(main_frame, text="Лабиринт", padx=10, pady=10)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=600, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        legend_frame = tk.Frame(canvas_frame)
        legend_frame.pack(fill=tk.X, pady=(10, 0))
        
        legend_items = [
            ("■", "black", "Стена"),
            ("■", "white", "Проход"),
            ("■", "blue", "Вход"),
            ("■", "red", "Выход"),
            ("■", "green", "Кратчайший путь"),
            ("■", "red", "Все пути (разные цвета)")
        ]
        
        for symbol, color, desc in legend_items:
            item_frame = tk.Frame(legend_frame)
            item_frame.pack(side=tk.LEFT, padx=5)
            tk.Label(item_frame, text=symbol, fg=color, font=("Arial", 12)).pack(side=tk.LEFT)
            tk.Label(item_frame, text=desc, font=("Arial", 8)).pack(side=tk.LEFT, padx=(2, 0))
    
    def create_maze(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width < 5 or height < 5:
                raise ValueError("Размеры должны быть не менее 5x5")
            
            self.maze_solver = MazeSolver(width, height)
            self.current_route = 0
            self.animation_running = False
            self.draw_maze()
            self.info_label.config(text="Лабиринт создан")
            self.shortest_length_label.config(text="Длина кратчайшего: -")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def generate_random(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            wall_density = int(self.wall_density_var.get())
            
            if width < 5 or height < 5:
                raise ValueError("Размеры должны быть не менее 5x5")
            
            self.maze_solver = MazeSolver(width, height)
            self.maze_solver.generate_random_maze(wall_density / 100.0)
            self.current_route = 0
            self.animation_running = False
            self.draw_maze()
            self.info_label.config(text=f"Случайный лабиринт создан\nПлотность стен: {wall_density}%")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def change_edit_mode(self):
        self.edit_mode = self.edit_mode_var.get()
    
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
        
        cell_x = canvas_y // self.cell_size
        cell_y = canvas_x // self.cell_size
        
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
    
    def draw_maze(self):
        if self.maze_solver is None:
            return
        
        self.canvas.delete("all")
        
        width = self.maze_solver.width
        height = self.maze_solver.height
        
        for i in range(height):
            for j in range(width):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if self.maze_solver.maze[i][j] == 1:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")
        
        if self.maze_solver.entrance:
            x, y = self.maze_solver.entrance
            x1 = y * self.cell_size
            y1 = x * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="blue")
            self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, 
                                   text="В", fill="white", font=("Arial", 10, "bold"))
        
        for exit_point in self.maze_solver.exits:
            x, y = exit_point
            x1 = y * self.cell_size
            y1 = x * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="red")
            self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, 
                                   text="В", fill="white", font=("Arial", 10, "bold"))
    
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
        
        self.info_label.config(text="Поиск кратчайших путей...")
        self.root.update()
        
        routes = self.maze_solver.find_all_routes()
        
        if routes:
            self.current_route = 0
            self.path_display_mode = "shortest"
            shortest_length = routes[0]['length']
            self.info_label.config(text=f"Найдено кратчайших путей: {len(routes)}")
            self.shortest_length_label.config(text=f"Длина кратчайшего: {shortest_length}")
            print(f"Обновлена длина кратчайшего: {shortest_length}")
            self.root.update()
            self.draw_routes()
        else:
            self.info_label.config(text="Пути не найдены")
            self.shortest_length_label.config(text="Длина кратчайшего: -")
            messagebox.showinfo("Результат", "Пути от входа до выходов не найдены")
    
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
        
        self.info_label.config(text="Поиск всех путей...\n(ограничено 100 путями)")
        self.root.update()
        
        try:
            routes = self.maze_solver.find_all_possible_routes()
            
            if routes:
                self.current_route = 0
                self.path_display_mode = "all"
                shortest_length = self.maze_solver.shortest_routes[0]['length'] if self.maze_solver.shortest_routes else 'N/A'
                self.info_label.config(text=f"Найдено путей: {len(routes)}\n"
                                          f"Кратчайших: {len(self.maze_solver.shortest_routes)}")
                self.shortest_length_label.config(text=f"Длина кратчайшего: {shortest_length}")
                self.root.update()
                self.draw_routes()
            else:
                self.info_label.config(text="Пути не найдены")
                self.shortest_length_label.config(text="Длина кратчайшего: -")
                messagebox.showinfo("Результат", "Пути от входа до выходов не найдены")
        except Exception as e:
            self.info_label.config(text="Ошибка при поиске путей")
            messagebox.showerror("Ошибка", f"Произошла ошибка при поиске путей: {e}")
    
    def draw_routes(self):
        if not self.maze_solver.all_routes:
            return
        
        self.draw_maze()
        
        routes_to_show = self.maze_solver.shortest_routes if self.path_display_mode == "shortest" else self.maze_solver.all_routes
        
        colors = [
            "red", "blue", "green", "purple", "orange", "brown", "pink", "cyan",
            "magenta", "lime", "navy", "olive", "teal", "maroon", "gold", "silver",
            "coral", "indigo", "violet", "turquoise", "salmon", "khaki", "plum",
            "tan", "crimson", "darkgreen", "darkblue", "darkred", "darkorange",
            "darkviolet", "darkcyan", "darkmagenta", "darkgoldenrod", "darkkhaki",
            "lightblue", "lightgreen", "lightcoral", "lightpink", "lightyellow",
            "lightgray", "lightsteelblue", "lightseagreen", "lightsalmon", "lightcyan"
        ]
        
        for i, route in enumerate(routes_to_show):
            if self.path_display_mode == "shortest":
                color = "green"
                width = 3
            else:
                if route in self.maze_solver.shortest_routes:
                    color = "green"
                    width = 3
                else:
                    color = colors[i % len(colors)]
                    width = 2
            
            for j in range(len(route['path']) - 1):
                x1, y1 = route['path'][j]
                x2, y2 = route['path'][j + 1]
                
                canvas_x1 = y1 * self.cell_size + self.cell_size // 2
                canvas_y1 = x1 * self.cell_size + self.cell_size // 2
                canvas_x2 = y2 * self.cell_size + self.cell_size // 2
                canvas_y2 = x2 * self.cell_size + self.cell_size // 2
                
                self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                                       fill=color, width=width)
    
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
        
        colors = [
            "red", "blue", "green", "purple", "orange", "brown", "pink", "cyan",
            "magenta", "lime", "navy", "olive", "teal", "maroon", "gold", "silver",
            "coral", "indigo", "violet", "turquoise", "salmon", "khaki", "plum",
            "tan", "crimson", "darkgreen", "darkblue", "darkred", "darkorange",
            "darkviolet", "darkcyan", "darkmagenta", "darkgoldenrod", "darkkhaki",
            "lightblue", "lightgreen", "lightcoral", "lightpink", "lightyellow",
            "lightgray", "lightsteelblue", "lightseagreen", "lightsalmon", "lightcyan"
        ]
        
        if route in self.maze_solver.shortest_routes:
            color = "green"
            width = 3
        else:
            color = colors[self.current_route % len(colors)]
            width = 2
        
        for j in range(len(route['path']) - 1):
            x1, y1 = route['path'][j]
            x2, y2 = route['path'][j + 1]
            
            canvas_x1 = y1 * self.cell_size + self.cell_size // 2
            canvas_y1 = x1 * self.cell_size + self.cell_size // 2
            canvas_x2 = y2 * self.cell_size + self.cell_size // 2
            canvas_y2 = x2 * self.cell_size + self.cell_size // 2
            
            self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                                   fill=color, width=width)
        
        self.info_label.config(text=f"Маршрут {self.current_route + 1}/{len(self.maze_solver.all_routes)}\n"
                                  f"Длина: {route['length']}\n"
                                  f"Выход: {route['exit']}")
    
    def show_all_paths(self):
        if self.maze_solver and self.maze_solver.all_routes:
            self.path_display_mode = "all"
            self.draw_routes()
            self.info_label.config(text=f"Показаны все пути: {len(self.maze_solver.all_routes)}")
            if self.maze_solver.shortest_routes:
                shortest_length = self.maze_solver.shortest_routes[0]['length']
                self.shortest_length_label.config(text=f"Длина кратчайшего: {shortest_length}")
    
    def show_shortest_paths(self):
        if self.maze_solver and self.maze_solver.shortest_routes:
            self.path_display_mode = "shortest"
            self.draw_routes()
            self.info_label.config(text=f"Показаны кратчайшие пути: {len(self.maze_solver.shortest_routes)}")
            shortest_length = self.maze_solver.shortest_routes[0]['length']
            self.shortest_length_label.config(text=f"Длина кратчайшего: {shortest_length}")
    
    def stop_animation(self):
        self.animation_running = False
    
    def clear_maze(self):
        if self.maze_solver:
            self.maze_solver.clear_maze()
            self.current_route = 0
            self.animation_running = False
            self.draw_maze()
            self.info_label.config(text="Лабиринт очищен")
            self.shortest_length_label.config(text="Длина кратчайшего: -")
    
    def save_maze(self):
        if self.maze_solver is None:
            messagebox.showwarning("Предупреждение", "Нет лабиринта для сохранения!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.maze_solver.save_maze(filename)
                self.info_label.config(text="Лабиринт сохранен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_maze(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.maze_solver = MazeSolver(1, 1)
                self.maze_solver.load_maze(filename)
                self.current_route = 0
                self.animation_running = False
                self.draw_maze()
                self.info_label.config(text="Лабиринт загружен")
                self.shortest_length_label.config(text="Длина кратчайшего: -")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

def main():
    root = tk.Tk()
    app = MazeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
