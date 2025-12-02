import tkinter as tk
from tkinter import messagebox
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
        
        from collections import deque
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

class SimpleMazeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабиринт")
        self.root.geometry("800x600")
        
        self.maze_solver = None
        self.cell_size = 25
        
        self.edit_mode = "wall"
        self.drawing = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Основной контейнер
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель управления слева
        control_frame = tk.Frame(main_frame, width=150)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Размеры лабиринта
        size_frame = tk.LabelFrame(control_frame, text="Размер лабиринта")
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(size_frame, text="Ширина:").pack(anchor=tk.W)
        self.width_var = tk.StringVar(value="20")
        tk.Entry(size_frame, textvariable=self.width_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        tk.Label(size_frame, text="Высота:").pack(anchor=tk.W)
        self.height_var = tk.StringVar(value="20")
        tk.Entry(size_frame, textvariable=self.height_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        tk.Button(size_frame, text="Создать", command=self.create_maze).pack(fill=tk.X, pady=2)
        
        # Генерация случайного лабиринта
        gen_frame = tk.LabelFrame(control_frame, text="Случайный лабиринт")
        gen_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(gen_frame, text="Плотность стен:").pack(anchor=tk.W)
        self.wall_density_var = tk.StringVar(value="30")
        tk.Scale(gen_frame, from_=10, to=70, orient=tk.HORIZONTAL, 
                variable=self.wall_density_var, length=130).pack(anchor=tk.W)
        
        tk.Button(gen_frame, text="Сгенерировать", command=self.generate_random).pack(fill=tk.X, pady=2)
        
        # Режимы редактирования
        edit_frame = tk.LabelFrame(control_frame, text="Режимы редактирования")
        edit_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.edit_mode_var = tk.StringVar(value="wall")
        
        tk.Radiobutton(edit_frame, text="Стена", variable=self.edit_mode_var, 
                      value="wall", command=self.change_edit_mode).pack(anchor=tk.W)
        tk.Radiobutton(edit_frame, text="Проход", variable=self.edit_mode_var, 
                      value="passage", command=self.change_edit_mode).pack(anchor=tk.W)
        tk.Radiobutton(edit_frame, text="Вход", variable=self.edit_mode_var, 
                      value="entrance", command=self.change_edit_mode).pack(anchor=tk.W)
        tk.Radiobutton(edit_frame, text="Выход", variable=self.edit_mode_var, 
                      value="exit", command=self.change_edit_mode).pack(anchor=tk.W)
        
        # Кнопки поиска
        search_frame = tk.LabelFrame(control_frame, text="Поиск путей")
        search_frame.pack(fill=tk.X)
        
        tk.Button(search_frame, text="Кратчайший путь", 
                 command=self.find_shortest_paths).pack(fill=tk.X, pady=2)
        tk.Button(search_frame, text="Все пути", 
                 command=self.find_all_paths).pack(fill=tk.X, pady=2)
        tk.Button(search_frame, text="Очистить", 
                 command=self.clear_maze).pack(fill=tk.X, pady=2)
        
        # Холст для лабиринта справа
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
    def create_maze(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width < 5 or height < 5:
                raise ValueError("Размеры должны быть не менее 5x5")
            
            self.maze_solver = MazeSolver(width, height)
            self.draw_maze()
            
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
            self.draw_maze()
            
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
        
        # Рисуем клетки
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
        
        # Рисуем вход
        if self.maze_solver.entrance:
            x, y = self.maze_solver.entrance
            x1 = y * self.cell_size
            y1 = x * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="blue")
        
        # Рисуем выходы
        for exit_point in self.maze_solver.exits:
            x, y = exit_point
            x1 = y * self.cell_size
            y1 = x * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="red")
    
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
        
        routes = self.maze_solver.find_all_routes()
        
        if routes:
            # Рисуем все кратчайшие пути
            self.draw_maze()
            for route in self.maze_solver.shortest_routes:
                self.draw_route(route['path'], "green")
            
            messagebox.showinfo("Результат", f"Найдено кратчайших путей: {len(self.maze_solver.shortest_routes)}\nДлина: {routes[0]['length']}")
        else:
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
        
        try:
            routes = self.maze_solver.find_all_possible_routes()
            
            if routes:
                # Рисуем все пути
                self.draw_maze()
                colors = ["red", "blue", "purple", "orange", "brown"]
                for i, route in enumerate(routes):
                    color = colors[i % len(colors)]
                    self.draw_route(route['path'], color)
                
                # Подсвечиваем кратчайшие пути зеленым поверх
                for route in self.maze_solver.shortest_routes:
                    self.draw_route(route['path'], "green", width=3)
                
                messagebox.showinfo("Результат", f"Найдено путей: {len(routes)}\nКратчайших: {len(self.maze_solver.shortest_routes)}")
            else:
                messagebox.showinfo("Результат", "Пути от входа до выходов не найдены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при поиске путей: {e}")
    
    def draw_route(self, path, color, width=2):
        for j in range(len(path) - 1):
            x1, y1 = path[j]
            x2, y2 = path[j + 1]
            
            canvas_x1 = y1 * self.cell_size + self.cell_size // 2
            canvas_y1 = x1 * self.cell_size + self.cell_size // 2
            canvas_x2 = y2 * self.cell_size + self.cell_size // 2
            canvas_y2 = x2 * self.cell_size + self.cell_size // 2
            
            self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                                   fill=color, width=width)
    
    def clear_maze(self):
        if self.maze_solver:
            self.maze_solver.clear_maze()
            self.draw_maze()

def main():
    root = tk.Tk()
    app = SimpleMazeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
