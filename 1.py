import tkinter as tk
from tkinter import ttk, messagebox
import time
from PIL import Image, ImageTk
import os

class KnightTourSolver:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.board = [[-1 for _ in range(m)] for _ in range(n)]
        self.moves = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]
    
    def is_valid_move(self, x, y):
        return 0 <= x < self.n and 0 <= y < self.m and self.board[x][y] == -1
    
    def get_valid_moves(self, x, y):
        valid_moves = []
        for dx, dy in self.moves:
            nx, ny = x + dx, y + dy
            if self.is_valid_move(nx, ny):
                count = 0
                for mx, my in self.moves:
                    nnx, nny = nx + mx, ny + my
                    if self.is_valid_move(nnx, nny):
                        count += 1
                valid_moves.append((nx, ny, count))
        return sorted(valid_moves, key=lambda x: x[2])
    
    def solve(self, start_x, start_y):
        self.board = [[-1 for _ in range(self.m)] for _ in range(self.n)]
        self.board[start_x][start_y] = 0
        
        if not self._solve_util(start_x, start_y, 1):
            return False
        return True
    
    def _solve_util(self, x, y, move_count):
        if move_count == self.n * self.m:
            return True
        
        next_moves = self.get_valid_moves(x, y)
        
        for nx, ny, _ in next_moves:
            self.board[nx][ny] = move_count
            if self._solve_util(nx, ny, move_count + 1):
                return True
            self.board[nx][ny] = -1
        
        return False

class KnightTourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Задача о ходе коня")
        self.root.geometry("800x600")
        
        self.n = 8
        self.m = 8
        self.start_x = 0
        self.start_y = 0
        self.solution = None
        self.current_step = 0
        self.animation_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Параметры доски", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Board size inputs
        ttk.Label(input_frame, text="Размер доски (n×m):").grid(row=0, column=0, sticky=tk.W)
        self.n_var = tk.StringVar(value="8")
        self.m_var = tk.StringVar(value="8")
        
        ttk.Entry(input_frame, textvariable=self.n_var, width=5).grid(row=0, column=1, padx=(5, 0))
        ttk.Label(input_frame, text="×").grid(row=0, column=2)
        ttk.Entry(input_frame, textvariable=self.m_var, width=5).grid(row=0, column=3, padx=(0, 10))
        
        # Start position inputs
        ttk.Label(input_frame, text="Начальная позиция:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
        self.start_x_var = tk.StringVar(value="0")
        self.start_y_var = tk.StringVar(value="0")
        
        ttk.Entry(input_frame, textvariable=self.start_x_var, width=5).grid(row=0, column=5, padx=(5, 0))
        ttk.Label(input_frame, text=",").grid(row=0, column=6)
        ttk.Entry(input_frame, textvariable=self.start_y_var, width=5).grid(row=0, column=7)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(button_frame, text="Найти решение", command=self.find_solution).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Показать анимацию", command=self.start_animation).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Сбросить", command=self.reset).pack(side=tk.LEFT)
        
        # Animation controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(control_frame, text="⏮️", command=self.first_step, width=3).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="⏪", command=self.prev_step, width=3).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="⏸️", command=self.pause_animation, width=3).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="▶️", command=self.resume_animation, width=3).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="⏩", command=self.next_step, width=3).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="⏭️", command=self.last_step, width=3).pack(side=tk.LEFT)
        
        # Speed control
        ttk.Label(control_frame, text="Скорость:").pack(side=tk.LEFT, padx=(20, 5))
        self.speed_var = tk.DoubleVar(value=0.5)
        ttk.Scale(control_frame, from_=0.1, to=2.0, variable=self.speed_var, 
                 orient=tk.HORIZONTAL, length=100).pack(side=tk.LEFT)
        
        # Canvas for board
        self.canvas = tk.Canvas(main_frame, bg='white', width=500, height=400)
        self.canvas.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Status bar
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
    def find_solution(self):
        try:
            self.n = int(self.n_var.get())
            self.m = int(self.m_var.get())
            self.start_x = int(self.start_x_var.get())
            self.start_y = int(self.start_y_var.get())
            
            if not (0 <= self.start_x < self.n and 0 <= self.start_y < self.m):
                messagebox.showerror("Ошибка", "Начальная позиция должна быть в пределах доски")
                return
            
            self.status_var.set("Поиск решения...")
            self.root.update()
            
            solver = KnightTourSolver(self.n, self.m)
            if solver.solve(self.start_x, self.start_y):
                self.solution = solver.board
                self.current_step = 0
                self.status_var.set(f"Решение найдено! Всего ходов: {self.n * self.m - 1}")
                self.draw_board()
            else:
                self.solution = None
                messagebox.showinfo("Результат", "Решение не найдено для данной конфигурации")
                self.status_var.set("Решение не найдено")
                
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")
            self.status_var.set("Ошибка ввода данных")
    
    def draw_board(self):
        self.canvas.delete("all")
        
        if not self.solution:
            return
        
        cell_size = min(400 // self.m, 400 // self.n, 40)
        board_width = self.m * cell_size
        board_height = self.n * cell_size
        
        # Draw board
        for i in range(self.n):
            for j in range(self.m):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                color = "#f0d9b5" if (i + j) % 2 == 0 else "#b58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                
                # Draw move number if this cell has been visited
                if self.solution[i][j] <= self.current_step and self.solution[i][j] >= 0:
                    self.canvas.create_text(x1 + cell_size//2, y1 + cell_size//2, 
                                          text=str(self.solution[i][j]), font=("Arial", 10, "bold"))
        
        # Draw knight
        for i in range(self.n):
            for j in range(self.m):
                if self.solution[i][j] == self.current_step:
                    x = j * cell_size + cell_size // 2
                    y = i * cell_size + cell_size // 2
                    radius = cell_size // 3
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, 
                                          fill="red", outline="darkred")
                    break
    
    def start_animation(self):
        if not self.solution:
            messagebox.showwarning("Предупреждение", "Сначала найдите решение")
            return
        
        self.animation_running = True
        self.animate()
    
    def animate(self):
        if not self.animation_running:
            return
        
        if self.current_step < self.n * self.m - 1:
            self.current_step += 1
            self.draw_board()
            self.root.update()
            delay = int(1000 / self.speed_var.get())
            self.root.after(delay, self.animate)
        else:
            self.animation_running = False
            self.status_var.set("Анимация завершена")
    
    def pause_animation(self):
        self.animation_running = False
    
    def resume_animation(self):
        if self.solution and self.current_step < self.n * self.m - 1:
            self.animation_running = True
            self.animate()
    
    def next_step(self):
        if self.solution and self.current_step < self.n * self.m - 1:
            self.current_step += 1
            self.draw_board()
    
    def prev_step(self):
        if self.solution and self.current_step > 0:
            self.current_step -= 1
            self.draw_board()
    
    def first_step(self):
        if self.solution:
            self.current_step = 0
            self.draw_board()
    
    def last_step(self):
        if self.solution:
            self.current_step = self.n * self.m - 1
            self.draw_board()
    
    def reset(self):
        self.solution = None
        self.current_step = 0
        self.animation_running = False
        self.canvas.delete("all")
        self.status_var.set("Готов к работе")

def main():
    root = tk.Tk()
    app = KnightTourApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
