import tkinter as tk
from tkinter import ttk, messagebox
from itertools import product
import copy

class ChessMateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Шахматы - Поиск матовых и патовых ситуаций")
        self.root.geometry("1000x700")
        
        self.board_size = 8
        self.cell_size = 70
        
        self.piece_symbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }
        
        self.board = [['' for _ in range(8)] for _ in range(8)]
        self.black_king_pos = None
        self.selected_pieces = []
        self.mate_positions = []
        self.pat_positions = []
        self.current_position_index = 0
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, padx=10)
        
        self.canvas = tk.Canvas(left_frame, width=self.cell_size*8, height=self.cell_size*8)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(right_frame, text="1. Выберите позицию черного короля", font=('Arial', 12, 'bold')).pack(pady=5)
        
        tk.Label(right_frame, text="2. Выберите две фигуры для белых:", font=('Arial', 12, 'bold')).pack(pady=5)
        
        pieces_frame = tk.Frame(right_frame)
        pieces_frame.pack(pady=5)
        
        self.piece_vars = []
        pieces = [('Ферзь', 'Q'), ('Ладья', 'R'), ('Слон', 'B'), ('Конь', 'N'), ('Пешка', 'P')]
        
        for i, (name, code) in enumerate(pieces):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(pieces_frame, text=f"{name} ({self.piece_symbols[code]})", 
                              variable=var, font=('Arial', 11),
                              command=lambda c=code, v=var: self.on_piece_select(c, v))
            cb.grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)
            self.piece_vars.append((code, var))
        
        tk.Button(right_frame, text="Найти все позиции", command=self.find_positions,
                 font=('Arial', 12), bg='#4CAF50', fg='white', padx=20, pady=10).pack(pady=10)
        
        stats_frame = tk.LabelFrame(right_frame, text="Статистика", font=('Arial', 11, 'bold'))
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.mate_label = tk.Label(stats_frame, text="Матовых позиций: 0", font=('Arial', 11))
        self.mate_label.pack(pady=2)
        
        self.pat_label = tk.Label(stats_frame, text="Патовых позиций: 0", font=('Arial', 11))
        self.pat_label.pack(pady=2)
        
        self.total_label = tk.Label(stats_frame, text="Всего позиций: 0", font=('Arial', 11))
        self.total_label.pack(pady=2)
        
        nav_frame = tk.LabelFrame(right_frame, text="Навигация по позициям", font=('Arial', 11, 'bold'))
        nav_frame.pack(fill=tk.X, pady=10)
        
        self.position_label = tk.Label(nav_frame, text="Позиция: 0 / 0", font=('Arial', 11))
        self.position_label.pack(pady=5)
        
        btn_frame = tk.Frame(nav_frame)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="◀◀ Первая", command=self.first_position,
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="◀ Пред.", command=self.prev_position,
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="След. ▶", command=self.next_position,
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Последняя ▶▶", command=self.last_position,
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        
        self.status_label = tk.Label(nav_frame, text="", font=('Arial', 11, 'bold'), fg='blue')
        self.status_label.pack(pady=5)
        
        tk.Button(right_frame, text="Сбросить", command=self.reset,
                 font=('Arial', 11), bg='#f44336', fg='white', padx=20, pady=5).pack(pady=10)
        
        self.draw_board()
    
    def draw_board(self):
        self.canvas.delete("all")
        colors = ['#F0D9B5', '#B58863']
        
        for row in range(8):
            for col in range(8):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
                
                if self.board[row][col]:
                    piece = self.board[row][col]
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                          text=self.piece_symbols[piece],
                                          font=('Arial', 48), fill='black' if piece.islower() else 'white')
        
        for i in range(8):
            self.canvas.create_text(i * self.cell_size + self.cell_size//2, 8 * self.cell_size + 15,
                                  text=chr(97 + i), font=('Arial', 12))
            self.canvas.create_text(-15, i * self.cell_size + self.cell_size//2,
                                  text=str(8 - i), font=('Arial', 12))
    
    def on_board_click(self, event):
        if self.mate_positions or self.pat_positions:
            return
            
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if 0 <= row < 8 and 0 <= col < 8:
            if self.black_king_pos == (row, col):
                self.board[row][col] = ''
                self.black_king_pos = None
            else:
                if self.black_king_pos:
                    old_row, old_col = self.black_king_pos
                    self.board[old_row][old_col] = ''
                
                self.board[row][col] = 'k'
                self.black_king_pos = (row, col)
            
            self.draw_board()
    
    def on_piece_select(self, code, var):
        selected = [c for c, v in self.piece_vars if v.get()]
        
        if len(selected) > 2:
            var.set(False)
            messagebox.showwarning("Предупреждение", "Можно выбрать только 2 фигуры!")
    
    def find_positions(self):
        if not self.black_king_pos:
            messagebox.showerror("Ошибка", "Выберите позицию черного короля!")
            return
        
        self.selected_pieces = [c for c, v in self.piece_vars if v.get()]
        
        if len(self.selected_pieces) != 2:
            messagebox.showerror("Ошибка", "Выберите ровно 2 фигуры!")
            return
        
        self.mate_positions = []
        self.pat_positions = []
        
        available_positions = []
        for row in range(8):
            for col in range(8):
                if (row, col) != self.black_king_pos:
                    available_positions.append((row, col))
        
        piece1, piece2 = self.selected_pieces
        
        total_checked = 0
        for pos1, pos2 in product(available_positions, repeat=2):
            if pos1 == pos2:
                continue
            
            if piece1 == piece2 and pos1 > pos2:
                continue
            
            if self.is_valid_position(pos1, pos2, piece1, piece2):
                board = [['' for _ in range(8)] for _ in range(8)]
                board[self.black_king_pos[0]][self.black_king_pos[1]] = 'k'
                board[pos1[0]][pos1[1]] = piece1
                board[pos2[0]][pos2[1]] = piece2
                
                white_king_pos = self.place_white_king(board)
                if white_king_pos:
                    board[white_king_pos[0]][white_king_pos[1]] = 'K'
                    
                    if self.is_checkmate(board):
                        self.mate_positions.append(copy.deepcopy(board))
                    elif self.is_stalemate(board):
                        self.pat_positions.append(copy.deepcopy(board))
            
            total_checked += 1
        
        self.update_stats()
        
        if self.mate_positions or self.pat_positions:
            self.current_position_index = 0
            self.show_current_position()
            messagebox.showinfo("Готово", f"Поиск завершен!\nНайдено {len(self.mate_positions)} матовых и {len(self.pat_positions)} патовых позиций.")
        else:
            messagebox.showinfo("Результат", "Не найдено ни одной матовой или патовой позиции.")
    
    def is_valid_position(self, pos1, pos2, piece1, piece2):
        if piece1 == 'B' and piece2 == 'B':
            color1 = (pos1[0] + pos1[1]) % 2
            color2 = (pos2[0] + pos2[1]) % 2
            if color1 == color2:
                return False
        return True
    
    def place_white_king(self, board):
        for row in range(8):
            for col in range(8):
                if board[row][col] == '':
                    if self.is_safe_for_white_king(board, row, col):
                        return (row, col)
        return None
    
    def is_safe_for_white_king(self, board, row, col):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if board[nr][nc] == 'k':
                        return False
        return True
    
    def is_checkmate(self, board):
        if not self.is_in_check(board, self.black_king_pos):
            return False
        
        return not self.has_legal_moves(board)
    
    def is_stalemate(self, board):
        if self.is_in_check(board, self.black_king_pos):
            return False
        
        return not self.has_legal_moves(board)
    
    def is_in_check(self, board, king_pos):
        row, col = king_pos
        
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.isupper():
                    if self.can_attack(board, (r, c), piece, king_pos):
                        return True
        return False
    
    def can_attack(self, board, from_pos, piece, to_pos):
        r1, c1 = from_pos
        r2, c2 = to_pos
        
        piece = piece.upper()
        
        if piece == 'Q':
            return self.can_attack_queen(board, r1, c1, r2, c2)
        elif piece == 'R':
            return self.can_attack_rook(board, r1, c1, r2, c2)
        elif piece == 'B':
            return self.can_attack_bishop(board, r1, c1, r2, c2)
        elif piece == 'N':
            return self.can_attack_knight(r1, c1, r2, c2)
        elif piece == 'K':
            return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1
        elif piece == 'P':
            return self.can_attack_pawn(r1, c1, r2, c2)
        
        return False
    
    def can_attack_rook(self, board, r1, c1, r2, c2):
        if r1 != r2 and c1 != c2:
            return False
        
        if r1 == r2:
            start, end = min(c1, c2), max(c1, c2)
            for c in range(start + 1, end):
                if board[r1][c]:
                    return False
        else:
            start, end = min(r1, r2), max(r1, r2)
            for r in range(start + 1, end):
                if board[r][c1]:
                    return False
        
        return True
    
    def can_attack_bishop(self, board, r1, c1, r2, c2):
        if abs(r1 - r2) != abs(c1 - c2):
            return False
        
        dr = 1 if r2 > r1 else -1
        dc = 1 if c2 > c1 else -1
        
        r, c = r1 + dr, c1 + dc
        while r != r2:
            if board[r][c]:
                return False
            r += dr
            c += dc
        
        return True
    
    def can_attack_queen(self, board, r1, c1, r2, c2):
        return self.can_attack_rook(board, r1, c1, r2, c2) or self.can_attack_bishop(board, r1, c1, r2, c2)
    
    def can_attack_knight(self, r1, c1, r2, c2):
        dr = abs(r1 - r2)
        dc = abs(c1 - c2)
        return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)
    
    def can_attack_pawn(self, r1, c1, r2, c2):
        if r2 != r1 - 1:
            return False
        if abs(c2 - c1) != 1:
            return False
        return True
    
    def has_legal_moves(self, board):
        kr, kc = self.black_king_pos
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                nr, nc = kr + dr, kc + dc
                
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board[nr][nc]
                    if not target or target.isupper():
                        test_board = copy.deepcopy(board)
                        test_board[kr][kc] = ''
                        test_board[nr][nc] = 'k'
                        
                        if not self.is_in_check(test_board, (nr, nc)):
                            return True
        
        return False
    
    def update_stats(self):
        self.mate_label.config(text=f"Матовых позиций: {len(self.mate_positions)}")
        self.pat_label.config(text=f"Патовых позиций: {len(self.pat_positions)}")
        self.total_label.config(text=f"Всего позиций: {len(self.mate_positions) + len(self.pat_positions)}")
    
    def show_current_position(self):
        all_positions = self.mate_positions + self.pat_positions
        
        if not all_positions:
            return
        
        if 0 <= self.current_position_index < len(all_positions):
            self.board = all_positions[self.current_position_index]
            self.draw_board()
            
            is_mate = self.current_position_index < len(self.mate_positions)
            status = "МАТ" if is_mate else "ПАТ"
            color = "red" if is_mate else "orange"
            
            self.status_label.config(text=status, fg=color)
            self.position_label.config(text=f"Позиция: {self.current_position_index + 1} / {len(all_positions)}")
    
    def first_position(self):
        if self.mate_positions or self.pat_positions:
            self.current_position_index = 0
            self.show_current_position()
    
    def prev_position(self):
        all_positions = self.mate_positions + self.pat_positions
        if all_positions and self.current_position_index > 0:
            self.current_position_index -= 1
            self.show_current_position()
    
    def next_position(self):
        all_positions = self.mate_positions + self.pat_positions
        if all_positions and self.current_position_index < len(all_positions) - 1:
            self.current_position_index += 1
            self.show_current_position()
    
    def last_position(self):
        all_positions = self.mate_positions + self.pat_positions
        if all_positions:
            self.current_position_index = len(all_positions) - 1
            self.show_current_position()
    
    def reset(self):
        self.board = [['' for _ in range(8)] for _ in range(8)]
        self.black_king_pos = None
        self.mate_positions = []
        self.pat_positions = []
        self.current_position_index = 0
        
        for code, var in self.piece_vars:
            var.set(False)
        
        self.update_stats()
        self.status_label.config(text="")
        self.position_label.config(text="Позиция: 0 / 0")
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessMateFinderApp(root)
    root.mainloop()

