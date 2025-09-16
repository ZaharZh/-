import tkinter as tk
from tkinter import ttk, messagebox

class KnightTourSolver:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.board = [[-1 for _ in range(m)] for _ in range(n)]
        self.moves = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]
        self.solutions = []
        self.solutions_count = 0
    
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
    
    def find_all_solutions(self, start_x, start_y):
        self.solutions = []
        self.solutions_count = 0
        self.board = [[-1 for _ in range(self.m)] for _ in range(self.n)]
        self.board[start_x][start_y] = 0
        
        self._find_all_solutions_util(start_x, start_y, 1)
        return self.solutions_count
    
    def _find_all_solutions_util(self, x, y, move_count):
        if move_count == self.n * self.m:
            # Сохраняем копию решения
            solution_copy = [row[:] for row in self.board]
            self.solutions.append(solution_copy)
            self.solutions_count += 1
            return
        
        next_moves = self.get_valid_moves(x, y)
        
        for nx, ny, _ in next_moves:
            self.board[nx][ny] = move_count
            self._find_all_solutions_util(nx, ny, move_count + 1)
            self.board[nx][ny] = -1
    
    def find_first_solution(self, start_x, start_y):
        self.board = [[-1 for _ in range(self.m)] for _ in range(self.n)]
        self.board[start_x][start_y] = 0
        
        if not self._find_first_solution_util(start_x, start_y, 1):
            return None
        return self.board
    
    def _find_first_solution_util(self, x, y, move_count):
        if move_count == self.n * self.m:
            return True
        
        next_moves = self.get_valid_moves(x, y)
        
        for nx, ny, _ in next_moves:
            self.board[nx][ny] = move_count
            if self._find_first_solution_util(nx, ny, move_count + 1):
                return True
            self.board[nx][ny] = -1
        
        return False

class KnightTourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Задача о ходе коня")
        self.root.geometry("700x550")
        
        self.n = 8
        self.m = 8
        self.start_x = 0
        self.start_y = 0
        self.solution = None
        self.solutions_count = 0
        self.current_solution_index = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Параметры доски", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Board size inputs
        ttk.Label(input_frame, text="Размер доски (n×m):").grid(row=0, column=0, sticky=tk.W)
        self.n_var = tk.StringVar(value="5")
        self.m_var = tk.StringVar(value="5")
        
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
        button_frame.grid(row=1, column=0, pady=(0, 10))
        
        ttk.Button(button_frame, text="Найти первое решение", command=self.find_first_solution).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Найти все решения", command=self.find_all_solutions).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Очистить", command=self.clear).pack(side=tk.LEFT)
        
        # Solutions navigation frame (скрыто изначально)
        self.nav_frame = ttk.Frame(main_frame)
        
        ttk.Button(self.nav_frame, text="◀ Предыдущее", command=self.prev_solution).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.nav_frame, text="Следующее ▶", command=self.next_solution).pack(side=tk.LEFT)
        
        # Info label
        self.info_label = ttk.Label(main_frame, text="", font=("Arial", 10))
        self.info_label.grid(row=3, column=0, pady=(5, 0))
        
        # Canvas for board
        self.canvas = tk.Canvas(main_frame, bg='white', width=500, height=400)
        self.canvas.grid(row=4, column=0, pady=(10, 0))
        
        # Status bar
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def find_first_solution(self):
        try:
            self.n = int(self.n_var.get())
            self.m = int(self.m_var.get())
            self.start_x = int(self.start_x_var.get())
            self.start_y = int(self.start_y_var.get())
            
            if not (0 <= self.start_x < self.n and 0 <= self.start_y < self.m):
                messagebox.showerror("Ошибка", "Начальная позиция должна быть в пределах доски")
                return
            
            self.status_var.set("Поиск первого решения...")
            self.root.update()
            
            solver = KnightTourSolver(self.n, self.m)
            solution = solver.find_first_solution(self.start_x, self.start_y)
            
            if solution:
                self.solution = solution
                self.solutions_count = 1
                self.current_solution_index = 0
                self.status_var.set("Первое решение найдено!")
                self.info_label.config(text="Решение 1 из 1")
                self.nav_frame.grid_forget()  # Скрываем навигацию
                self.draw_board()
            else:
                self.solution = None
                messagebox.showinfo("Результат", "Решение не найдено для данной конфигурации")
                self.status_var.set("Решение не найдено")
                self.canvas.delete("all")
                self.info_label.config(text="")
                
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")
            self.status_var.set("Ошибка ввода данных")
    
    def find_all_solutions(self):
        try:
            self.n = int(self.n_var.get())
            self.m = int(self.m_var.get())
            self.start_x = int(self.start_x_var.get())
            self.start_y = int(self.start_y_var.get())
            
            if not (0 <= self.start_x < self.n and 0 <= self.start_y < self.m):
                messagebox.showerror("Ошибка", "Начальная позиция должна быть в пределах доски")
                return
            
            if self.n * self.m > 25:  # Предупреждение для больших досок
                if not messagebox.askyesno("Предупреждение", 
                                         f"Доска {self.n}×{self.m} имеет {self.n * self.m} клеток.\n"
                                         f"Поиск всех решений может занять много времени.\n"
                                         f"Продолжить?"):
                    return
            
            self.status_var.set("Поиск всех решений...")
            self.root.update()
            
            solver = KnightTourSolver(self.n, self.m)
            solutions_count = solver.find_all_solutions(self.start_x, self.start_y)
            
            if solutions_count > 0:
                self.solutions_count = solutions_count
                self.solver = solver
                self.current_solution_index = 0
                self.solution = self.solver.solutions[0]
                
                self.status_var.set(f"Найдено решений: {solutions_count}")
                self.info_label.config(text=f"Решение 1 из {solutions_count}")
                
                # Показываем навигацию если решений больше 1
                if solutions_count > 1:
                    self.nav_frame.grid(row=2, column=0, pady=(5, 0))
                else:
                    self.nav_frame.grid_forget()
                
                self.draw_board()
            else:
                self.solution = None
                messagebox.showinfo("Результат", "Решения не найдены для данной конфигурации")
                self.status_var.set("Решения не найдены")
                self.canvas.delete("all")
                self.info_label.config(text="")
                self.nav_frame.grid_forget()
                
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")
            self.status_var.set("Ошибка ввода данных")
        except RecursionError:
            messagebox.showerror("Ошибка", "Слишком большая доска для рекурсивного поиска")
            self.status_var.set("Ошибка: слишком глубокая рекурсия")
    
    def next_solution(self):
        if self.solutions_count > 1 and self.current_solution_index < self.solutions_count - 1:
            self.current_solution_index += 1
            self.solution = self.solver.solutions[self.current_solution_index]
            self.info_label.config(text=f"Решение {self.current_solution_index + 1} из {self.solutions_count}")
            self.draw_board()
    
    def prev_solution(self):
        if self.solutions_count > 1 and self.current_solution_index > 0:
            self.current_solution_index -= 1
            self.solution = self.solver.solutions[self.current_solution_index]
            self.info_label.config(text=f"Решение {self.current_solution_index + 1} из {self.solutions_count}")
            self.draw_board()
    
    def draw_board(self):
        self.canvas.delete("all")
        
        if not self.solution:
            return
        
        cell_size = min(400 // self.m, 400 // self.n, 40)
        
        # Draw board
        for i in range(self.n):
            for j in range(self.m):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                color = "#f0d9b5" if (i + j) % 2 == 0 else "#b58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                
                # Draw move number
                if self.solution[i][j] >= 0:
                    self.canvas.create_text(x1 + cell_size//2, y1 + cell_size//2, 
                                          text=str(self.solution[i][j]), font=("Arial", 10, "bold"))
        
        # Draw knight on starting position
        x = self.start_y * cell_size + cell_size // 2
        y = self.start_x * cell_size + cell_size // 2
        radius = cell_size // 3
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, 
                              fill="red", outline="darkred")
    
    def clear(self):
        self.solution = None
        self.solutions_count = 0
        self.current_solution_index = 0
        self.canvas.delete("all")
        self.status_var.set("Готов к работе")
        self.info_label.config(text="")
        self.nav_frame.grid_forget()

def main():
    root = tk.Tk()
    app = KnightTourApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
