import tkinter as tk
from tkinter import ttk, messagebox
import struct
from typing import List

class AES:
    """
    Реализация AES-128 (128-битный ключ, 10 раундов)
    Без использования сторонних библиотек
    """
    
    # Предварительно вычисленные таблицы для оптимизации
    
    # Таблица S-box (прямая)
    SBOX = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ]
    
    # Таблица обратного S-box (для дешифрования)
    INV_SBOX = [
        0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
        0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
        0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
        0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
        0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
        0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
        0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
        0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
        0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
        0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
        0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
        0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
        0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
        0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
        0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
        0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
    ]
    
    # Константы для Key Expansion (Rcon)
    RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
    
    def __init__(self, key: bytes):
        """
        Инициализация AES с ключом (16 байт для AES-128)
        """
        if len(key) != 16:
            raise ValueError("Для AES-128 ключ должен быть 16 байт (128 бит)")
        
        self.key = key
        self.round_keys = self._key_expansion(key)
    
    def _key_expansion(self, key: bytes) -> List[List[int]]:
        """
        Расширение ключа для AES-128
        Генерирует 11 раундовых ключей (44 слова по 32 бита)
        """
        w = [0] * 44
        
        # Первые 4 слова - это сам ключ
        for i in range(4):
            w[i] = (key[4*i] << 24) | (key[4*i+1] << 16) | (key[4*i+2] << 8) | key[4*i+3]
        
        # Генерация остальных слов
        for i in range(4, 44):
            temp = w[i-1]
            
            if i % 4 == 0:
                # RotWord, SubWord и Rcon
                temp = ((temp << 8) & 0xFFFFFFFF) | (temp >> 24)
                temp = (
                    (self.SBOX[(temp >> 24) & 0xFF] << 24) |
                    (self.SBOX[(temp >> 16) & 0xFF] << 16) |
                    (self.SBOX[(temp >> 8) & 0xFF] << 8) |
                    self.SBOX[temp & 0xFF]
                )
                temp ^= (self.RCON[i//4 - 1] << 24)
            
            w[i] = w[i-4] ^ temp
        
        # Преобразуем в матрицу 11x4x4 для удобства
        round_keys = []
        for round_num in range(11):
            round_key = []
            for col in range(4):
                word = w[round_num*4 + col]
                round_key.extend([
                    (word >> 24) & 0xFF,
                    (word >> 16) & 0xFF,
                    (word >> 8) & 0xFF,
                    word & 0xFF
                ])
            round_keys.append(round_key)
        
        return round_keys
    
    def _sub_bytes(self, state: List[int]) -> List[int]:
        """Операция SubBytes - замена каждого байта через S-box"""
        return [self.SBOX[b] for b in state]
    
    def _inv_sub_bytes(self, state: List[int]) -> List[int]:
        """Обратная операция SubBytes"""
        return [self.INV_SBOX[b] for b in state]
    
    def _shift_rows(self, state: List[int]) -> List[int]:
        """Операция ShiftRows - циклический сдвиг строк матрицы состояния"""
        result = [0] * 16
        
        # Строка 0: без сдвига
        result[0], result[4], result[8], result[12] = state[0], state[4], state[8], state[12]
        
        # Строка 1: сдвиг на 1
        result[1], result[5], result[9], result[13] = state[5], state[9], state[13], state[1]
        
        # Строка 2: сдвиг на 2
        result[2], result[6], result[10], result[14] = state[10], state[14], state[2], state[6]
        
        # Строка 3: сдвиг на 3
        result[3], result[7], result[11], result[15] = state[15], state[3], state[7], state[11]
        
        return result
    
    def _inv_shift_rows(self, state: List[int]) -> List[int]:
        """Обратная операция ShiftRows - сдвиг вправо"""
        result = [0] * 16
        
        # Первая строка без изменений
        result[0], result[4], result[8], result[12] = state[0], state[4], state[8], state[12]
        
        # Вторая строка: сдвиг на 1 вправо
        result[1], result[5], result[9], result[13] = state[13], state[1], state[5], state[9]
        
        # Третья строка: сдвиг на 2 вправо
        result[2], result[6], result[10], result[14] = state[10], state[14], state[2], state[6]
        
        # Четвертая строка: сдвиг на 3 вправо
        result[3], result[7], result[11], result[15] = state[7], state[11], state[15], state[3]
        
        return result
    
    def _mix_columns(self, state: List[int]) -> List[int]:
        """Операция MixColumns - перемешивание столбцов"""
        def gmul(a: int, b: int) -> int:
            """Умножение в поле Галуа GF(2^8)"""
            p = 0
            for _ in range(8):
                if b & 1:
                    p ^= a
                hi_bit_set = a & 0x80
                a = (a << 1) & 0xFF
                if hi_bit_set:
                    a ^= 0x1B  # Полином x^8 + x^4 + x^3 + x + 1
                b >>= 1
            return p
        
        result = [0] * 16
        
        for i in range(4):  # Для каждого столбца
            col_start = i * 4
            s0, s1, s2, s3 = (
                state[col_start],
                state[col_start + 1],
                state[col_start + 2],
                state[col_start + 3]
            )
            
            result[col_start] = gmul(0x02, s0) ^ gmul(0x03, s1) ^ s2 ^ s3
            result[col_start + 1] = s0 ^ gmul(0x02, s1) ^ gmul(0x03, s2) ^ s3
            result[col_start + 2] = s0 ^ s1 ^ gmul(0x02, s2) ^ gmul(0x03, s3)
            result[col_start + 3] = gmul(0x03, s0) ^ s1 ^ s2 ^ gmul(0x02, s3)
        
        return result
    
    def _inv_mix_columns(self, state: List[int]) -> List[int]:
        """Обратная операция MixColumns"""
        def gmul(a: int, b: int) -> int:
            p = 0
            for _ in range(8):
                if b & 1:
                    p ^= a
                hi_bit_set = a & 0x80
                a = (a << 1) & 0xFF
                if hi_bit_set:
                    a ^= 0x1B
                b >>= 1
            return p
        
        result = [0] * 16
        
        for i in range(4):
            col_start = i * 4
            s0, s1, s2, s3 = (
                state[col_start],
                state[col_start + 1],
                state[col_start + 2],
                state[col_start + 3]
            )
            
            result[col_start] = gmul(0x0e, s0) ^ gmul(0x0b, s1) ^ gmul(0x0d, s2) ^ gmul(0x09, s3)
            result[col_start + 1] = gmul(0x09, s0) ^ gmul(0x0e, s1) ^ gmul(0x0b, s2) ^ gmul(0x0d, s3)
            result[col_start + 2] = gmul(0x0d, s0) ^ gmul(0x09, s1) ^ gmul(0x0e, s2) ^ gmul(0x0b, s3)
            result[col_start + 3] = gmul(0x0b, s0) ^ gmul(0x0d, s1) ^ gmul(0x09, s2) ^ gmul(0x0e, s3)
        
        return result
    
    def _add_round_key(self, state: List[int], round_key: List[int]) -> List[int]:
        """Операция AddRoundKey - XOR состояния с ключом раунда"""
        return [state[i] ^ round_key[i] for i in range(16)]
    
    def encrypt_block(self, plaintext: bytes) -> bytes:
        """
        Шифрование одного блока (16 байт)
        """
        if len(plaintext) != 16:
            raise ValueError("Блок должен быть 16 байт (128 бит)")
        
        state = list(plaintext)
        
        # Начальный раунд: только AddRoundKey
        state = self._add_round_key(state, self.round_keys[0])
        
        # Основные раунды (1-9)
        for round_num in range(1, 10):
            state = self._sub_bytes(state)
            state = self._shift_rows(state)
            state = self._mix_columns(state)
            state = self._add_round_key(state, self.round_keys[round_num])
        
        # Финальный раунд (10) - без MixColumns
        state = self._sub_bytes(state)
        state = self._shift_rows(state)
        state = self._add_round_key(state, self.round_keys[10])
        
        return bytes(state)
    
    def decrypt_block(self, ciphertext: bytes) -> bytes:
        """
        Дешифрование одного блока (16 байт)
        """
        if len(ciphertext) != 16:
            raise ValueError("Блок должен быть 16 байт (128 бит)")
        
        state = list(ciphertext)
        
        # Финальный раунд в обратном порядке
        state = self._add_round_key(state, self.round_keys[10])
        state = self._inv_shift_rows(state)
        state = self._inv_sub_bytes(state)
        
        # Основные раунды в обратном порядке (9-1)
        for round_num in range(9, 0, -1):
            state = self._add_round_key(state, self.round_keys[round_num])
            state = self._inv_mix_columns(state)
            state = self._inv_shift_rows(state)
            state = self._inv_sub_bytes(state)
        
        # Начальный раунд
        state = self._add_round_key(state, self.round_keys[0])
        
        return bytes(state)
    
    def encrypt_ecb(self, data: bytes) -> bytes:
        """
        Шифрование в режиме ECB (Educational purposes only!)
        """
        # Дополнение PKCS#7
        pad_len = 16 - (len(data) % 16)
        padded_data = data + bytes([pad_len] * pad_len)
        
        encrypted = b''
        for i in range(0, len(padded_data), 16):
            block = padded_data[i:i+16]
            encrypted += self.encrypt_block(block)
        
        return encrypted
    
    def decrypt_ecb(self, data: bytes) -> bytes:
        """
        Дешифрование в режиме ECB
        """
        if len(data) % 16 != 0:
            raise ValueError("Данные должны быть кратны 16 байтам")
        
        decrypted = b''
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            decrypted += self.decrypt_block(block)
        
        # Убираем дополнение PKCS#7
        pad_len = decrypted[-1]
        if pad_len < 1 or pad_len > 16:
            raise ValueError("Неверное дополнение")
        
        return decrypted[:-pad_len]


class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Шифрование текста AES-128")
        self.root.geometry("900x700")
        
        # Переменные
        self.key_var = tk.StringVar(value="MySecretKey12345")  # 16 символов для AES-128
        
        # Создание виджетов
        self.create_widgets()
        
    def create_widgets(self):
        # Стиль
        style = ttk.Style()
        style.configure("TButton", padding=8, font=("Arial", 11))
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TLabelframe.Label", font=("Arial", 12, "bold"))
        
        # Фрейм для исходного текста
        input_frame = ttk.LabelFrame(self.root, text="Исходный текст", padding=15)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.input_text = tk.Text(input_frame, height=8, font=("Courier", 11), wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для управления с увеличенным полем ключа
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=15, pady=(25, 15))
        
        # Фрейм для ключа шифрования
        key_frame = ttk.Frame(control_frame)
        key_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 30))
        
        ttk.Label(key_frame, text="Ключ шифрования (16 символов):", font=("Arial", 12)).pack(anchor=tk.W, pady=(0, 8))
        
        # Увеличенное поле для ввода ключа
        self.key_entry = ttk.Entry(
            key_frame, 
            textvariable=self.key_var, 
            width=25,
            font=("Arial", 12)
        )
        self.key_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(button_frame, text="").pack(pady=(0, 10))
        
        # Кнопки с увеличенными отступами
        buttons_frame = ttk.Frame(button_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(
            buttons_frame, 
            text="Зашифровать", 
            command=self.encrypt,
            width=15
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame, 
            text="Расшифровать", 
            command=self.decrypt,
            width=15
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame, 
            text="Очистить все", 
            command=self.clear_all,
            width=15
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame, 
            text="Пример работы", 
            command=self.show_example,
            width=15
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Фрейм для зашифрованного текста
        encrypted_frame = ttk.LabelFrame(self.root, text="Зашифрованный текст (hex)", padding=15)
        encrypted_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.encrypted_text = tk.Text(
            encrypted_frame, 
            height=8, 
            font=("Courier", 11), 
            bg="#f5f5f5",
            wrap=tk.WORD
        )
        self.encrypted_text.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для расшифрованного текста
        decrypted_frame = ttk.LabelFrame(self.root, text="Расшифрованный текст", padding=15)
        decrypted_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 15))
        
        self.decrypted_text = tk.Text(
            decrypted_frame, 
            height=8, 
            font=("Courier", 11), 
            bg="#f5f5f5",
            wrap=tk.WORD
        )
        self.decrypted_text.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем скроллбары для текстовых полей
        for text_widget in [self.input_text, self.encrypted_text, self.decrypted_text]:
            scrollbar = ttk.Scrollbar(text_widget)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=text_widget.yview)
        
        # Информационная метка
        info_label = ttk.Label(
            self.root, 
            text="Алгоритм: AES-128 | Режим: ECB | Ключ: 16 байт (128 бит)",
            font=("Arial", 10, "italic")
        )
        info_label.pack(side=tk.BOTTOM, pady=5)
        
        # Настройка привязки событий
        self.key_entry.bind("<Return>", lambda event: self.encrypt())
        
    def prepare_key(self, key_str: str) -> bytes:
        """
        Подготовка ключа: преобразование строки в 16 байт
        """
        # Преобразуем строку в байты
        key_bytes = key_str.encode('utf-8')
        
        # Если ключ короче 16 байт, дополняем нулями
        if len(key_bytes) < 16:
            key_bytes = key_bytes.ljust(16, b'\0')
        # Если ключ длиннее 16 байт, обрезаем
        elif len(key_bytes) > 16:
            key_bytes = key_bytes[:16]
        
        return key_bytes
    
    def encrypt(self):
        """Шифрование текста с использованием AES-128"""
        try:
            text = self.input_text.get("1.0", tk.END).strip()
            key_str = self.key_var.get().strip()
            
            if not text:
                messagebox.showwarning("Предупреждение", "Введите текст для шифрования")
                return
            
            if not key_str:
                messagebox.showwarning("Предупреждение", "Введите ключ шифрования")
                return
            
            # Проверяем длину ключа
            if len(key_str) < 16:
                if not messagebox.askyesno("Предупреждение", 
                                         f"Ключ слишком короткий ({len(key_str)} символов).\n"
                                         f"Для AES-128 требуется 16 символов.\n"
                                         "Дополнить нулями?"):
                    return
            
            # Подготавливаем ключ
            key = self.prepare_key(key_str)
            
            # Создаем объект AES
            aes = AES(key)
            
            # Шифруем текст
            encrypted_bytes = aes.encrypt_ecb(text.encode('utf-8'))
            
            # Преобразуем в hex для отображения
            encrypted_hex = encrypted_bytes.hex()
            
            # Отображаем результат
            self.encrypted_text.delete("1.0", tk.END)
            self.encrypted_text.insert("1.0", encrypted_hex)
            
            # Автоматически очищаем поле расшифрованного текста
            self.decrypted_text.delete("1.0", tk.END)
            
            # Показываем информацию о размере
            messagebox.showinfo("Успех", 
                              f"Текст успешно зашифрован!\n"
                              f"Исходный размер: {len(text.encode('utf-8'))} байт\n"
                              f"Зашифрованный размер: {len(encrypted_bytes)} байт")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка при шифровании: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка: {str(e)}")
    
    def decrypt(self):
        """Расшифрование текста с использованием AES-128"""
        try:
            hex_text = self.encrypted_text.get("1.0", tk.END).strip()
            key_str = self.key_var.get().strip()
            
            if not hex_text:
                messagebox.showwarning("Предупреждение", "Введите зашифрованный текст в hex формате")
                return
            
            if not key_str:
                messagebox.showwarning("Предупреждение", "Введите ключ шифрования")
                return
            
            # Проверяем hex формат
            try:
                encrypted_bytes = bytes.fromhex(hex_text)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат hex строки")
                return
            
            # Подготавливаем ключ
            key = self.prepare_key(key_str)
            
            # Создаем объект AES
            aes = AES(key)
            
            # Дешифруем текст
            decrypted_bytes = aes.decrypt_ecb(encrypted_bytes)
            
            # Преобразуем в строку
            try:
                decrypted_text = decrypted_bytes.decode('utf-8')
            except UnicodeDecodeError:
                messagebox.showerror("Ошибка", "Не удалось расшифровать текст. Возможно, неверный ключ.")
                return
            
            # Отображаем результат
            self.decrypted_text.delete("1.0", tk.END)
            self.decrypted_text.insert("1.0", decrypted_text)
            
            messagebox.showinfo("Успех", "Текст успешно расшифрован!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка при расшифровании: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка: {str(e)}")
    
    def clear_all(self):
        """Очистка всех полей"""
        self.input_text.delete("1.0", tk.END)
        self.encrypted_text.delete("1.0", tk.END)
        self.decrypted_text.delete("1.0", tk.END)
        self.key_var.set("MySecretKey12345")
        self.key_entry.focus_set()
    
    def show_example(self):
        """Показать пример работы алгоритма"""
        example_text = """Пример работы AES-128 шифрования:

Алгоритм AES (Advanced Encryption Standard) - это симметричный блочный шифр, принятый в качестве стандарта в США в 2001 году.

Основные характеристики AES-128:
• Длина ключа: 128 бит (16 байт)
• Длина блока: 128 бит (16 байт)
• Количество раундов: 10

Пример шифрования:
Ключ: "MySecretKey12345"
Текст: "Привет, мир! Это тест AES шифрования."

Зашифрованный текст будет представлен в hex формате."""
        
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", "Привет, мир! Это тест AES шифрования.")
        self.key_var.set("MySecretKey12345")
        
        # Автоматически шифруем пример
        self.encrypt()


def main():
    root = tk.Tk()
    app = EncryptionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
