import tkinter as tk
from tkinter import scrolledtext, messagebox
import random
import math

# ---------- RSA функции ----------
def is_prime(n: int) -> bool:
    """Проверка числа на простоту перебором делителей."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = int(math.sqrt(n)) + 1
    for i in range(3, limit, 2):
        if n % i == 0:
            return False
    return True

def generate_prime(min_val: int, max_val: int) -> int:
    """Генерирует случайное простое число в заданном диапазоне."""
    primes = [i for i in range(min_val, max_val + 1) if is_prime(i)]
    if not primes:
        raise ValueError("В указанном диапазоне нет простых чисел")
    return random.choice(primes)

def gcd(a: int, b: int) -> int:
    """Наибольший общий делитель."""
    return math.gcd(a, b)

def modinv(a: int, m: int) -> int:
    """Находит обратное число к a по модулю m (расширенный алгоритм Евклида)."""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Обратного элемента не существует")
    return x % m

def egcd(a: int, b: int):
    """Расширенный алгоритм Евклида."""
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y

def generate_keys():
    """Генерирует открытый и закрытый ключи RSA."""
    # Выбираем два разных простых числа в диапазоне 100-500
    p = generate_prime(100, 500)
    q = generate_prime(100, 500)
    while q == p:
        q = generate_prime(100, 500)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e: обычно 65537, но проверяем взаимную простоту с phi
    e = 65537
    if gcd(e, phi) != 1:
        # Если 65537 не подходит, подбираем другое e
        for candidate in [17, 257, 65537]:
            if gcd(candidate, phi) == 1:
                e = candidate
                break
        else:
            # Если ничего не подошло, перебираем нечётные числа, начиная с 3
            e = 3
            while gcd(e, phi) != 1:
                e += 2
    
    d = modinv(e, phi)
    return (n, e), (n, d)

def encrypt(text: str, n: int, e: int) -> str:
    """Шифрует текст: каждый символ -> число, возводится в степень e по модулю n."""
    encrypted_numbers = []
    for ch in text:
        m = ord(ch)
        if m >= n:
            raise ValueError(f"Символ '{ch}' имеет код {m}, который больше или равен модулю n={n}. Увеличьте простые числа.")
        c = pow(m, e, n)
        encrypted_numbers.append(str(c))
    return " ".join(encrypted_numbers)

def decrypt(cipher_text: str, n: int, d: int) -> str:
    """Дешифрует текст: числа -> возводятся в степень d по модулю n -> символы."""
    if not cipher_text.strip():
        return ""
    parts = cipher_text.strip().split()
    decrypted_chars = []
    for part in parts:
        try:
            c = int(part)
        except ValueError:
            raise ValueError(f"Неверный формат зашифрованного текста: ожидалось число, получено '{part}'")
        m = pow(c, d, n)
        decrypted_chars.append(chr(m))
    return "".join(decrypted_chars)

# ---------- GUI ----------
class RSAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RSA Шифрование")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Генерация ключей при запуске
        self.pub_key, self.priv_key = generate_keys()
        self.n, self.e = self.pub_key
        self.n_priv, self.d = self.priv_key

        # Создание виджетов
        self.create_widgets()

    def create_widgets(self):
        # Поле ввода текста
        tk.Label(self.root, text="Входной текст (для шифрования или расшифрования):").pack(pady=(10, 0))
        self.input_text = scrolledtext.ScrolledText(self.root, height=5, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        # Ключи
        frame_keys = tk.Frame(self.root)
        frame_keys.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_keys, text="Открытый ключ (n, e):").grid(row=0, column=0, sticky=tk.W)
        self.pub_key_var = tk.StringVar(value=f"n={self.n}, e={self.e}")
        self.pub_key_entry = tk.Entry(frame_keys, textvariable=self.pub_key_var, state='readonly', width=30)
        self.pub_key_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_keys, text="Закрытый ключ (n, d):").grid(row=1, column=0, sticky=tk.W)
        self.priv_key_var = tk.StringVar(value=f"n={self.n_priv}, d={self.d}")
        self.priv_key_entry = tk.Entry(frame_keys, textvariable=self.priv_key_var, state='readonly', width=30)
        self.priv_key_entry.grid(row=1, column=1, padx=5, pady=2)

        # Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.encrypt_btn = tk.Button(btn_frame, text="Зашифровать", command=self.encrypt_text, width=15)
        self.encrypt_btn.pack(side=tk.LEFT, padx=5)

        self.decrypt_btn = tk.Button(btn_frame, text="Расшифровать", command=self.decrypt_text, width=15)
        self.decrypt_btn.pack(side=tk.LEFT, padx=5)

        # Поле вывода зашифрованного текста
        tk.Label(self.root, text="Зашифрованный текст:").pack()
        self.encrypted_text = scrolledtext.ScrolledText(self.root, height=5, wrap=tk.WORD)
        self.encrypted_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        # Поле вывода расшифрованного текста
        tk.Label(self.root, text="Расшифрованный текст:").pack()
        self.decrypted_text = scrolledtext.ScrolledText(self.root, height=5, wrap=tk.WORD)
        self.decrypted_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

    def encrypt_text(self):
        """Обработчик кнопки 'Зашифровать'."""
        plain = self.input_text.get("1.0", tk.END).rstrip("\n")
        if not plain:
            messagebox.showwarning("Предупреждение", "Введите текст для шифрования.")
            return
        try:
            encrypted = encrypt(plain, self.n, self.e)
            self.encrypted_text.delete("1.0", tk.END)
            self.encrypted_text.insert("1.0", encrypted)
        except Exception as e:
            messagebox.showerror("Ошибка шифрования", str(e))

    def decrypt_text(self):
        """Обработчик кнопки 'Расшифровать'."""
        cipher = self.input_text.get("1.0", tk.END).rstrip("\n")
        if not cipher:
            messagebox.showwarning("Предупреждение", "Введите зашифрованный текст для расшифрования.")
            return
        try:
            decrypted = decrypt(cipher, self.n_priv, self.d)
            self.decrypted_text.delete("1.0", tk.END)
            self.decrypted_text.insert("1.0", decrypted)
        except Exception as e:
            messagebox.showerror("Ошибка расшифрования", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = RSAApp(root)
    root.mainloop()
