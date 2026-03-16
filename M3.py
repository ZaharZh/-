import tkinter as tk
from tkinter import scrolledtext, messagebox
import struct

# ---------- MD5 реализация (без hashlib) ----------

def left_rotate(x, n):
    """Циклический сдвиг влево 32-битного числа на n бит."""
    return ((x << n) & 0xFFFFFFFF) | (x >> (32 - n))

def md5(message: bytes) -> bytes:
    """
    Вычисляет MD5-хеш от входных байтов.
    Возвращает 16-байтовый дайджест (little-endian порядок).
    """
    # Константы для раундов (T[i] = floor(2^32 * abs(sin(i+1))), i от 0 до 63)
    T = [
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
        0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
        0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
        0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
        0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
        0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
    ]

    # Количество бит для сдвига в каждом раунде (s[i])
    shifts = [
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
    ]

    # Инициализация буферов (A, B, C, D) в little-endian (как в спецификации)
    A = 0x67452301
    B = 0xefcdab89
    C = 0x98badcfe
    D = 0x10325476

    # Padding: добавляем бит '1' (0x80), затем нули, затем 64-битная длина в битах
    orig_len_in_bits = (8 * len(message)) & 0xFFFFFFFFFFFFFFFF  # длина в битах, 64 бита
    message += b'\x80'
    # Добавляем нули, пока длина сообщения в байтах не станет такой, что (len + 8) % 64 == 0
    while (len(message) % 64) != 56:
        message += b'\x00'
    # Добавляем длину (64 бита, little-endian)
    message += struct.pack('<Q', orig_len_in_bits)  # <Q = unsigned long long little-endian

    # Обработка блоков по 512 бит (64 байта)
    for i in range(0, len(message), 64):
        block = message[i:i+64]
        # Разбиваем блок на 16 слов по 32 бита (little-endian)
        X = list(struct.unpack('<16I', block))

        # Сохраняем текущие значения буферов
        AA, BB, CC, DD = A, B, C, D

        # Раунд 1
        for j in range(16):
            # F = (B & C) | (~B & D)
            F = (B & C) | ((~B) & D)
            g = j
            temp = (A + F + X[g] + T[j]) & 0xFFFFFFFF
            A, B, C, D = D, (B + left_rotate(temp, shifts[j])) & 0xFFFFFFFF, B, C

        # Раунд 2
        for j in range(16, 32):
            # G = (D & B) | (~D & C)
            G = (D & B) | ((~D) & C)
            g = (5*j + 1) % 16
            temp = (A + G + X[g] + T[j]) & 0xFFFFFFFF
            A, B, C, D = D, (B + left_rotate(temp, shifts[j])) & 0xFFFFFFFF, B, C

        # Раунд 3
        for j in range(32, 48):
            # H = B ^ C ^ D
            H = B ^ C ^ D
            g = (3*j + 5) % 16
            temp = (A + H + X[g] + T[j]) & 0xFFFFFFFF
            A, B, C, D = D, (B + left_rotate(temp, shifts[j])) & 0xFFFFFFFF, B, C

        # Раунд 4
        for j in range(48, 64):
            # I = C ^ (B | ~D)
            I = C ^ (B | (~D))
            g = (7*j) % 16
            temp = (A + I + X[g] + T[j]) & 0xFFFFFFFF
            A, B, C, D = D, (B + left_rotate(temp, shifts[j])) & 0xFFFFFFFF, B, C

        # Обновляем буферы
        A = (A + AA) & 0xFFFFFFFF
        B = (B + BB) & 0xFFFFFFFF
        C = (C + CC) & 0xFFFFFFFF
        D = (D + DD) & 0xFFFFFFFF

    # Финальный дайджест (16 байт, little-endian)
    return struct.pack('<4I', A, B, C, D)

def compute_md5(text: str) -> str:
    """Вычисляет MD5-хеш от переданной строки и возвращает его в шестнадцатеричном виде."""
    message_bytes = text.encode('utf-8')
    digest_bytes = md5(message_bytes)
    return digest_bytes.hex()

# ---------- GUI ----------
class MD5App:
    def __init__(self, root):
        self.root = root
        self.root.title("MD5 Хеширование (собственная реализация)")
        self.root.geometry("500x300")
        self.root.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        # Поле ввода текста
        tk.Label(self.root, text="Введите текст для вычисления MD5-хеша:").pack(pady=(10, 0))
        self.input_text = scrolledtext.ScrolledText(self.root, height=5, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        # Кнопка вычисления
        self.compute_btn = tk.Button(self.root, text="Вычислить MD5", command=self.compute_hash, width=20)
        self.compute_btn.pack(pady=10)

        # Поле вывода результата
        tk.Label(self.root, text="MD5-хеш:").pack()
        self.output_text = scrolledtext.ScrolledText(self.root, height=2, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

    def compute_hash(self):
        """Обработчик кнопки: читает текст, вычисляет MD5 и выводит результат."""
        plain = self.input_text.get("1.0", tk.END).rstrip("\n")
        if not plain:
            messagebox.showwarning("Предупреждение", "Введите текст для хеширования.")
            return
        try:
            hash_value = compute_md5(plain)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", hash_value)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MD5App(root)
    root.mainloop()
