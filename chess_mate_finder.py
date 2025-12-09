import tkinter as tk
from tkinter import ttk, messagebox
from itertools import product
import copy

class ChessMateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("♛ Шахматный анализатор - Поиск матовых и патовых позиций")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Настройка стиля
        self.setup_styles()
        
        self.board_size = 8
        self.cell_size = 75
        
        self.piece_symbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }
        
        self.piece_names = {
            'K': 'Король', 'Q': 'Ферзь', 'R': 'Ладья', 'B': 'Слон', 'N': 'Конь', 'P': 'Пешка'
        }
        
        self.board = [['' for _ in range(8)] for _ in range(8)]
        self.black_king_pos = None
        self.selected_pieces = []
        self.mate_positions = []
        self.pat_positions = []
        self.current_position_index = 0
        self.showing_mates = True
        
        self.setup_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цветовая схема
        self.colors = {
            'bg': '#f0f0f0',
            'card_bg': '#ffffff',
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'board_light': '#f0d9b5',
            'board_dark': '#b58863',
            'text': '#2c3e50'
        }
        
    def setup_ui(self):
        # Заголовок
        title_frame = tk.Frame(self.root, bg=self.colors['primary'], height=60)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="♛ ШАХМАТНЫЙ АНАЛИЗАТОР",
                              font=('Arial', 20, 'bold'),
                              fg='white',
                              bg=self.colors['primary'])
        title_label.pack(expand=True)
        
        sub_title = tk.Label(title_frame,
                            text="Поиск матовых и патовых позиций для двух фигур",
                            font=('Arial', 11),
                            fg='#bdc3c7',
                            bg=self.colors['primary'])
        sub_title.pack(pady=(0, 10))
        
        # Основной контейнер
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Левая панель - доска
        left_panel = tk.Frame(main_container, bg=self.colors['bg'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 20))
        
        # Карточка доски
        board_card = tk.Frame(left_panel, bg='white', relief=tk.RAISED, bd=2)
        board_card.pack(fill=tk.BOTH, expand=True)
        
        board_label = tk.Label(board_card, 
                              text="ШАХМАТНАЯ ДОСКА",
                              font=('Arial', 14, 'bold'),
                              bg='white',
                              fg=self.colors['primary'])
        board_label.pack(pady=15)
        
        self.canvas = tk.Canvas(board_card, 
                               width=self.cell_size*8, 
                               height=self.cell_size*8,
                               bg='white',
                               highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        instructions = tk.Label(board_card,
                               text="Нажмите на клетку, чтобы установить черного короля",
                               font=('Arial', 10),
                               bg='white',
                               fg=self.colors['text'])
        instructions.pack(pady=10)
        
        # Правая панель - управление
        right_panel = tk.Frame(main_container, bg=self.colors['bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Выбор фигур
        pieces_card = tk.Frame(right_panel, bg='white', relief=tk.RAISED, bd=2)
        pieces_card.pack(fill=tk.X, pady=(0, 15))
        
        pieces_title = tk.Label(pieces_card,
                               text="1. ВЫБЕРИТЕ ФИГУРЫ БЕЛЫХ",
                               font=('Arial', 12, 'bold'),
                               bg='white',
                               fg=self.colors['primary'])
        pieces_title.pack(pady=15)
        
        pieces_subtitle = tk.Label(pieces_card,
                                  text="Выберите ровно две фигуры (дублирование разрешено):",
                                  font=('Arial', 10),
                                  bg='white',
                                  fg=self.colors['text'])
        pieces_subtitle.pack()
        
        pieces_container = tk.Frame(pieces_card, bg='white')
        pieces_container.pack(pady=15, padx=20)
        
        self.piece_vars = []
        pieces = [('Q', 'Ферзь'), ('R', 'Ладья'), ('B', 'Слон'), ('N', 'Конь'), ('P', 'Пешка')]
        
        for i, (code, name) in enumerate(pieces):
            frame = tk.Frame(pieces_container, bg='white')
            frame.grid(row=i//3, column=i%3, padx=10, pady=5, sticky='w')
            
            var = tk.BooleanVar()
            
            # Стилизованная кнопка вместо checkbox
            btn = tk.Button(frame,
                           text=f"{self.piece_symbols[code]} {name}",
                           font=('Arial', 11),
                           bg='white',
                           fg=self.colors['text'],
                           relief=tk.RAISED,
                           bd=1,
                           padx=10,
                           pady=5,
                           command=lambda c=code, v=var: self.toggle_piece(c, v))
            btn.pack()
            
            self.piece_vars.append((code, var, btn))
        
        # Кнопка поиска
        action_frame = tk.Frame(right_panel, bg=self.colors['bg'])
        action_frame.pack(fill=tk.X, pady=15)
        
        self.find_btn = tk.Button(action_frame,
                                 text="🔍 НАЙТИ ВСЕ ПОЗИЦИИ",
                                 font=('Arial', 13, 'bold'),
                                 bg=self.colors['success'],
                                 fg='white',
                                 padx=30,
                                 pady=12,
                                 command=self.find_positions)
        self.find_btn.pack()
        
        # Статистика
        stats_card = tk.Frame(right_panel, bg='white', relief=tk.RAISED, bd=2)
        stats_card.pack(fill=tk.X, pady=(0, 15))
        
        stats_title = tk.Label(stats_card,
                              text="СТАТИСТИКА",
                              font=('Arial', 12, 'bold'),
                              bg='white',
                              fg=self.colors['primary'])
        stats_title.pack(pady=15)
        
        stats_grid = tk.Frame(stats_card, bg='white')
        stats_grid.pack(pady=10, padx=20)
        
        # Матовые позиции
        mate_frame = tk.Frame(stats_grid, bg='white')
        mate_frame.grid(row=0, column=0, padx=10, pady=5)
        
        self.mate_count = tk.Label(mate_frame,
                                  text="0",
                                  font=('Arial', 24, 'bold'),
                                  bg='white',
                                  fg=self.colors['danger'])
        self.mate_count.pack()
        
        tk.Label(mate_frame,
                text="МАТОВЫХ",
                font=('Arial', 10),
                bg='white',
                fg=self.colors['text']).pack()
        
        # Патовые позиции
        pat_frame = tk.Frame(stats_grid, bg='white')
        pat_frame.grid(row=0, column=1, padx=10, pady=5)
        
        self.pat_count = tk.Label(pat_frame,
                                 text="0",
                                 font=('Arial', 24, 'bold'),
                                 bg='white',
                                 fg=self.colors['warning'])
        self.pat_count.pack()
        
        tk.Label(pat_frame,
                text="ПАТОВЫХ",
                font=('Arial', 10),
                bg='white',
                fg=self.colors['text']).pack()
        
        # Всего позиций
        total_frame = tk.Frame(stats_grid, bg='white')
        total_frame.grid(row=0, column=2, padx=10, pady=5)
        
        self.total_count = tk.Label(total_frame,
                                   text="0",
                                   font=('Arial', 24, 'bold'),
                                   bg='white',
                                   fg=self.colors['secondary'])
        self.total_count.pack()
        
        tk.Label(total_frame,
                text="ВСЕГО",
                font=('Arial', 10),
                bg='white',
                fg=self.colors['text']).pack()
        
        # Навигация
        nav_card = tk.Frame(right_panel, bg='white', relief=tk.RAISED, bd=2)
        nav_card.pack(fill=tk.X, pady=(0, 15))
        
        nav_title = tk.Label(nav_card,
                            text="НАВИГАЦИЯ ПО РЕЗУЛЬТАТАМ",
                            font=('Arial', 12, 'bold'),
                            bg='white',
                            fg=self.colors['primary'])
        nav_title.pack(pady=15)
        
        # Фильтр типа позиций
        filter_frame = tk.Frame(nav_card, bg='white')
        filter_frame.pack(pady=5)
        
        tk.Label(filter_frame,
                text="Показать:",
                font=('Arial', 10),
                bg='white',
                fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_var = tk.StringVar(value="all")
        
        tk.Radiobutton(filter_frame,
                      text="Все",
                      variable=self.filter_var,
                      value="all",
                      font=('Arial', 10),
                      bg='white',
                      command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(filter_frame,
                      text="Только мат",
                      variable=self.filter_var,
                      value="mate",
                      font=('Arial', 10),
                      bg='white',
                      fg=self.colors['danger'],
                      command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(filter_frame,
                      text="Только пат",
                      variable=self.filter_var,
                      value="pat",
                      font=('Arial', 10),
                      bg='white',
                      fg=self.colors['warning'],
                      command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        
        # Позиция и статус
        pos_frame = tk.Frame(nav_card, bg='white')
        pos_frame.pack(pady=10)
        
        self.position_label = tk.Label(pos_frame,
                                      text="Позиция: 0 / 0",
                                      font=('Arial', 11, 'bold'),
                                      bg='white',
                                      fg=self.colors['text'])
        self.position_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.status_label = tk.Label(pos_frame,
                                    text="",
                                    font=('Arial', 12, 'bold'),
                                    bg='white')
        self.status_label.pack(side=tk.LEFT)
        
        # Кнопки навигации
        nav_buttons = tk.Frame(nav_card, bg='white')
        nav_buttons.pack(pady=15)
        
        button_style = {'font': ('Arial', 10), 'padx': 15, 'pady': 8}
        
        tk.Button(nav_buttons,
                 text="⏮ Первая",
                 bg=self.colors['light'],
                 command=self.first_position,
                 **button_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(nav_buttons,
                 text="◀ Предыдущая",
                 bg=self.colors['light'],
                 command=self.prev_position,
                 **button_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(nav_buttons,
                 text="Следующая ▶",
                 bg=self.colors['light'],
                 command=self.next_position,
                 **button_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(nav_buttons,
                 text="Последняя ⏭",
                 bg=self.colors['light'],
                 command=self.last_position,
                 **button_style).pack(side=tk.LEFT, padx=2)
        
        # Информация о текущих фигурах
        info_frame = tk.Frame(nav_card, bg='white')
        info_frame.pack(pady=10)
        
        self.current_pieces_label = tk.Label(info_frame,
                                            text="Фигуры: не выбраны",
                                            font=('Arial', 10),
                                            bg='white',
                                            fg=self.colors['text'])
        self.current_pieces_label.pack()
        
        # Кнопка сброса
        reset_frame = tk.Frame(right_panel, bg=self.colors['bg'])
        reset_frame.pack(fill=tk.X)
        
        tk.Button(reset_frame,
                 text="🔄 СБРОС ВСЕХ НАСТРОЕК",
                 font=('Arial', 11),
                 bg=self.colors['danger'],
                 fg='white',
                 padx=20,
                 pady=10,
                 command=self.reset).pack()
        
        self.draw_board()
    
    def toggle_piece(self, code, var):
        selected = [c for c, v, _ in self.piece_vars if v.get()]
        
        if var.get():
            if len(selected) > 2:
                var.set(False)
                messagebox.showwarning("Предупреждение", "Можно выбрать только 2 фигуры!")
                return
            # Подсветка выбранной фигуры
            for c, v, btn in self.piece_vars:
                if c == code and v.get():
                    btn.configure(bg=self.colors['secondary'], fg='white')
        else:
            # Сброс подсветки
            for c, v, btn in self.piece_vars:
                if c == code:
                    btn.configure(bg='white', fg=self.colors['text'])
        
        self.update_pieces_label()
    
    def update_pieces_label(self):
        selected = [c for c, v, _ in self.piece_vars if v.get()]
        if selected:
            names = [self.piece_names.get(p, p) for p in selected]
            self.current_pieces_label.config(
                text=f"Выбраны: {', '.join(names)} ({', '.join([self.piece_symbols[p] for p in selected])})",
                fg=self.colors['success']
            )
        else:
            self.current_pieces_label.config(
                text="Фигуры: не выбраны",
                fg=self.colors['text']
            )
    
    def draw_board(self):
        self.canvas.delete("all")
        colors = [self.colors['board_light'], self.colors['board_dark']]
        
        # Рисуем клетки
        for row in range(8):
            for col in range(8):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='', width=0)
                
                # Подсветка черного короля
                if self.black_king_pos and (row, col) == self.black_king_pos:
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                               fill='#e74c3c', 
                                               outline='', 
                                               width=0)
                    self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, 
                                               fill=color, 
                                               outline='', 
                                               width=0)
                
                # Рисуем фигуры
                if self.board[row][col]:
                    piece = self.board[row][col]
                    self.canvas.create_text(x1 + self.cell_size//2, 
                                          y1 + self.cell_size//2,
                                          text=self.piece_symbols[piece],
                                          font=('Segoe UI Symbol', 40),
                                          fill='black' if piece.islower() else 'white')
        
        # Рисуем координаты
        for i in range(8):
            # Буквы внизу
            self.canvas.create_text(i * self.cell_size + self.cell_size//2, 
                                  8 * self.cell_size + 15,
                                  text=chr(97 + i), 
                                  font=('Arial', 11, 'bold'),
                                  fill=self.colors['text'])
            # Цифры слева
            self.canvas.create_text(-15, 
                                  i * self.cell_size + self.cell_size//2,
                                  text=str(8 - i), 
                                  font=('Arial', 11, 'bold'),
                                  fill=self.colors['text'])
    
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
    
    def find_positions(self):
        if not self.black_king_pos:
            messagebox.showerror("Ошибка", "Выберите позицию черного короля!")
            return
        
        self.selected_pieces = [c for c, v, _ in self.piece_vars if v.get()]
        
        if len(self.selected_pieces) != 2:
            messagebox.showerror("Ошибка", "Выберите ровно 2 фигуры!")
            return
        
        self.find_btn.config(text="🔍 ИДЕТ ПОИСК...", state=tk.DISABLED)
        self.root.update()
        
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
        self.find_btn.config(text="🔍 НАЙТИ ВСЕ ПОЗИЦИИ", state=tk.NORMAL)
        
        if self.mate_positions or self.pat_positions:
            self.current_position_index = 0
            self.show_current_position()
            messagebox.showinfo("Готово", 
                              f"Поиск завершен!\n\n"
                              f"✓ Матовых позиций: {len(self.mate_positions)}\n"
                              f"✓ Патовых позиций: {len(self.pat_positions)}\n"
                              f"✓ Всего найдено: {len(self.mate_positions) + len(self.pat_positions)}")
        else:
            messagebox.showinfo("Результат", 
                              "Не найдено ни одной матовой или патовой позиции для выбранной комбинации фигур.")
    
    def apply_filter(self):
        filter_type = self.filter_var.get()
        if filter_type == "mate":
            self.showing_mates = True
            if self.mate_positions:
                self.current_position_index = 0
                self.show_current_position()
        elif filter_type == "pat":
            self.showing_mates = False
            if self.pat_positions:
                self.current_position_index = 0
                self.show_current_position()
        else:
            # "all" - показываем все
            all_positions = self.mate_positions + self.pat_positions
            if all_positions:
                self.show_current_position()
    
    def show_current_position(self):
        filter_type = self.filter_var.get()
        
        if filter_type == "mate":
            positions = self.mate_positions
            total = len(self.mate_positions)
        elif filter_type == "pat":
            positions = self.pat_positions
            total = len(self.pat_positions)
        else:
            positions = self.mate_positions + self.pat_positions
            total = len(positions)
        
        if not positions:
            self.board = [['' for _ in range(8)] for _ in range(8)]
            if self.black_king_pos:
                self.board[self.black_king_pos[0]][self.black_king_pos[1]] = 'k'
            self.draw_board()
            self.position_label.config(text="Позиция: 0 / 0")
            self.status_label.config(text="")
            return
        
        if self.current_position_index >= len(positions):
            self.current_position_index = 0
        
        self.board = positions[self.current_position_index]
        self.draw_board()
        
        # Определяем тип позиции
        if filter_type == "all":
            is_mate = self.current_position_index < len(self.mate_positions)
            status = "МАТ" if is_mate else "ПАТ"
            color = self.colors['danger'] if is_mate else self.colors['warning']
        else:
            status = "МАТ" if filter_type == "mate" else "ПАТ"
            color = self.colors['danger'] if filter_type == "mate" else self.colors['warning']
        
        # Создаем стилизованную метку статуса
        self.status_label.config(text=f"  {status}  ", 
                                fg='white', 
                                bg=color,
                                font=('Arial', 11, 'bold'))
        
        self.position_label.config(text=f"Позиция: {self.current_position_index + 1} / {total}")
    
    def update_stats(self):
        mate_count = len(self.mate_positions)
        pat_count = len(self.pat_positions)
        total_count = mate_count + pat_count
        
        self.mate_count.config(text=str(mate_count))
        self.pat_count.config(text=str(pat_count))
        self.total_count.config(text=str(total_count))
    
    # Остальные методы остаются без изменений
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
    
    def first_position(self):
        filter_type = self.filter_var.get()
        if filter_type == "mate" and self.mate_positions:
            self.current_position_index = 0
        elif filter_type == "pat" and self.pat_positions:
            self.current_position_index = 0
        elif filter_type == "all" and (self.mate_positions or self.pat_positions):
            self.current_position_index = 0
        self.show_current_position()
    
    def prev_position(self):
        filter_type = self.filter_var.get()
        positions = []
        
        if filter_type == "mate":
            positions = self.mate_positions
        elif filter_type == "pat":
            positions = self.pat_positions
        else:
            positions = self.mate_positions + self.pat_positions
        
        if positions and self.current_position_index > 0:
            self.current_position_index -= 1
            self.show_current_position()
    
    def next_position(self):
        filter_type = self.filter_var.get()
        positions = []
        
        if filter_type == "mate":
            positions = self.mate_positions
        elif filter_type == "pat":
            positions = self.pat_positions
        else:
            positions = self.mate_positions + self.pat_positions
        
        if positions and self.current_position_index < len(positions) - 1:
            self.current_position_index += 1
            self.show_current_position()
    
    def last_position(self):
        filter_type = self.filter_var.get()
        positions = []
        
        if filter_type == "mate":
            positions = self.mate_positions
        elif filter_type == "pat":
            positions = self.pat_positions
        else:
            positions = self.mate_positions + self.pat_positions
        
        if positions:
            self.current_position_index = len(positions) - 1
            self.show_current_position()
    
    def reset(self):
        self.board = [['' for _ in range(8)] for _ in range(8)]
        self.black_king_pos = None
        self.mate_positions = []
        self.pat_positions = []
        self.current_position_index = 0
        self.filter_var.set("all")
        
        for code, var, btn in self.piece_vars:
            var.set(False)
            btn.configure(bg='white', fg=self.colors['text'])
        
        self.update_stats()
        self.status_label.config(text="", bg='white')
        self.position_label.config(text="Позиция: 0 / 0")
        self.current_pieces_label.config(text="Фигуры: не выбраны", fg=self.colors['text'])
        self.find_btn.config(text="🔍 НАЙТИ ВСЕ ПОЗИЦИИ", state=tk.NORMAL)
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessMateFinderApp(root)
    root.mainloop()
