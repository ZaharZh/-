import tkinter as tk
from tkinter import ttk, messagebox
import rsa
import hashlib
import random

class RSAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RSA шифрование")
        self.root.geometry("800x500")
        self.root.minsize(600, 400)

        # Переменная для пароля
        self.password_var = tk.StringVar(value="my_secure_password")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Поле ввода текста
        input_frame = ttk.LabelFrame(main_frame, text="Входной текст", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.input_text = tk.Text(input_frame, height=8, font=("Courier", 11), wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        input_scroll = ttk.Scrollbar(self.input_text)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.config(yscrollcommand=input_scroll.set)
        input_scroll.config(command=self.input_text.yview)

        # Панель с паролем и кнопками
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        # Поле для пароля
        pass_frame = ttk.Frame(control_frame)
        pass_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(pass_frame, text="Пароль (для генерации RSA-ключей):", font=("Arial", 11)).pack(anchor=tk.W)
        self.pass_entry = ttk.Entry(pass_frame, textvariable=self.password_var, font=("Arial", 11), width=30)
        self.pass_entry.pack(fill=tk.X, pady=(5, 0))

        # Кнопки
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.RIGHT, padx=(20, 0))

        self.encrypt_btn = ttk.Button(btn_frame, text="Зашифровать", command=self.encrypt, width=15)
        self.encrypt_btn.pack(side=tk.LEFT, padx=5)

        self.decrypt_btn = ttk.Button(btn_frame, text="Расшифровать", command=self.decrypt, width=15)
        self.decrypt_btn.pack(side=tk.LEFT, padx=5)

        # Поле вывода результата
        output_frame = ttk.LabelFrame(main_frame, text="Результат", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.output_text = tk.Text(output_frame, height=8, font=("Courier", 11), wrap=tk.WORD, bg="#f5f5f5")
        self.output_text.pack(fill=tk.BOTH, expand=True)

        output_scroll = ttk.Scrollbar(self.output_text)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=output_scroll.set)
        output_scroll.config(command=self.output_text.yview)

        # Информация
        info_label = ttk.Label(
            main_frame,
            text="RSA (1024 бит). Зашифрованный текст отображается в hex. Длина сообщения ограничена (≈117 байт).",
            font=("Arial", 9, "italic")
        )
        info_label.pack(pady=(5, 0))

        self.pass_entry.bind("<Return>", lambda e: self.encrypt())

    def generate_keys_from_password(self, password: str):
        """
        Детерминированная генерация RSA-ключей на основе пароля.
        Используется хеш пароля как seed для ГПСЧ.
        """
        # Получаем seed как число из хеша пароля
        seed = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        rng = random.Random(seed)

        # Функция randfunc, которую требует rsa.newkeys
        def randfunc(n):
            return bytes([rng.getrandbits(8) for _ in range(n)])

        # Генерируем ключи длиной 1024 бита
        (pubkey, privkey) = rsa.newkeys(1024, randfunc)
        return pubkey, privkey

    def encrypt(self):
        """Шифрование текста из верхнего поля"""
        try:
            text = self.input_text.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Предупреждение", "Введите текст для шифрования.")
                return

            password = self.pass_entry.get().strip()
            if not password:
                messagebox.showwarning("Предупреждение", "Введите пароль.")
                return

            pubkey, _ = self.generate_keys_from_password(password)

            # Кодируем сообщение в байты
            message_bytes = text.encode('utf-8')

            # RSA может зашифровать только сообщение, длина которого меньше длины ключа в байтах минус padding
            # Для 1024 бит и PKCS#1 v1.5 максимум — 117 байт.
            if len(message_bytes) > 117:
                messagebox.showerror("Ошибка", f"Сообщение слишком длинное ({len(message_bytes)} байт).\n"
                                                "Максимум 117 байт для RSA 1024 бит с PKCS#1.")
                return

            encrypted = rsa.encrypt(message_bytes, pubkey)
            hex_result = encrypted.hex()

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", hex_result)

        except rsa.pkcs1.CryptoError as e:
            messagebox.showerror("Ошибка шифрования", f"Ошибка RSA: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка:\n{str(e)}")

    def decrypt(self):
        """Расшифрование hex-строки из верхнего поля"""
        try:
            hex_str = self.input_text.get("1.0", tk.END).strip()
            if not hex_str:
                messagebox.showwarning("Предупреждение", "Введите зашифрованный текст (hex) для расшифровки.")
                return

            password = self.pass_entry.get().strip()
            if not password:
                messagebox.showwarning("Предупреждение", "Введите пароль.")
                return

            _, privkey = self.generate_keys_from_password(password)

            # Проверка и преобразование hex в байты
            try:
                encrypted_bytes = bytes.fromhex(hex_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введённый текст не является корректной hex-строкой.")
                return

            # Расшифровываем
            decrypted_bytes = rsa.decrypt(encrypted_bytes, privkey)

            # Пытаемся декодировать в UTF-8
            try:
                decrypted_text = decrypted_bytes.decode('utf-8')
            except UnicodeDecodeError:
                decrypted_text = str(decrypted_bytes)  # если не текст, показываем байты

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", decrypted_text)

        except rsa.pkcs1.DecryptionError:
            messagebox.showerror("Ошибка", "Не удалось расшифровать. Возможно, неверный пароль или повреждённые данные.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка:\n{str(e)}")


def main():
    root = tk.Tk()
    app = RSAApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
