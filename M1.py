import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

# ============ КЛАСС AES (без изменений) ============
class AES:
    # ... (полностью тот же код, что и ранее) ...
    # Для краткости здесь не повторяю, но он должен быть таким же, как в предыдущем ответе.
    # Полный код класса AES смотрите в предыдущем сообщении.
    pass

# ============ УПРОЩЕННЫЙ ИНТЕРФЕЙС ============
class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AES-128 шифрование")
        self.root.geometry("800x500")
        self.root.minsize(600, 400)
        
        # Переменная для ключа
        self.key_var = tk.StringVar(value="MySecretKey12345")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поле ввода текста
        input_frame = ttk.LabelFrame(main_frame, text="Входной текст", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.input_text = tk.Text(input_frame, height=8, font=("Courier", 11), wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар для входного текста
        input_scroll = ttk.Scrollbar(self.input_text)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.config(yscrollcommand=input_scroll.set)
        input_scroll.config(command=self.input_text.yview)
        
        # Панель с ключом и кнопками
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Поле для ключа
        key_frame = ttk.Frame(control_frame)
        key_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(key_frame, text="Ключ (16 символов):", font=("Arial", 11)).pack(anchor=tk.W)
        self.key_entry = ttk.Entry(key_frame, textvariable=self.key_var, font=("Arial", 11), width=30)
        self.key_entry.pack(fill=tk.X, pady=(5, 0))
        
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
        
        # Скроллбар для выходного текста
        output_scroll = ttk.Scrollbar(self.output_text)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=output_scroll.set)
        output_scroll.config(command=self.output_text.yview)
        
        # Информационная строка
        info_label = ttk.Label(
            main_frame,
            text="AES-128, режим ECB. Зашифрованный текст отображается в hex.",
            font=("Arial", 9, "italic")
        )
        info_label.pack(pady=(5, 0))
        
        # Привязка Enter к шифрованию
        self.key_entry.bind("<Return>", lambda e: self.encrypt())
        
    def prepare_key(self, key_str: str) -> bytes:
        """Преобразует строку ключа в 16 байт (дополняет нулями или обрезает)"""
        key_bytes = key_str.encode('utf-8')
        if len(key_bytes) < 16:
            key_bytes = key_bytes.ljust(16, b'\0')
        elif len(key_bytes) > 16:
            key_bytes = key_bytes[:16]
        return key_bytes
    
    def encrypt(self):
        """Шифрование текста из поля ввода"""
        try:
            text = self.input_text.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Предупреждение", "Введите текст для шифрования.")
                return
            
            key_str = self.key_var.get().strip()
            if not key_str:
                messagebox.showwarning("Предупреждение", "Введите ключ шифрования.")
                return
            
            # Проверка длины ключа
            if len(key_str) < 16:
                if not messagebox.askyesno("Ключ короткий",
                                          f"Длина ключа {len(key_str)} символов. Для AES-128 нужно 16 символов.\n"
                                          "Дополнить нулями?"):
                    return
            
            key = self.prepare_key(key_str)
            aes = AES(key)
            
            # Шифруем
            encrypted = aes.encrypt_ecb(text.encode('utf-8'))
            hex_result = encrypted.hex()
            
            # Очищаем поле вывода и вставляем результат
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", hex_result)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при шифровании:\n{str(e)}")
    
    def decrypt(self):
        """Расшифрование hex-строки из поля ввода"""
        try:
            hex_str = self.input_text.get("1.0", tk.END).strip()
            if not hex_str:
                messagebox.showwarning("Предупреждение", "Введите зашифрованный текст (hex) для расшифровки.")
                return
            
            key_str = self.key_var.get().strip()
            if not key_str:
                messagebox.showwarning("Предупреждение", "Введите ключ шифрования.")
                return
            
            # Проверка, что введённый текст - корректный hex
            try:
                encrypted_bytes = bytes.fromhex(hex_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введённый текст не является корректной hex-строкой.")
                return
            
            key = self.prepare_key(key_str)
            aes = AES(key)
            
            # Дешифруем
            decrypted_bytes = aes.decrypt_ecb(encrypted_bytes)
            
            # Пытаемся декодировать в UTF-8
            try:
                decrypted_text = decrypted_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # Если не получается, показываем как есть (возможно, бинарные данные)
                decrypted_text = str(decrypted_bytes)
            
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", decrypted_text)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка при расшифровании:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка:\n{str(e)}")


def main():
    root = tk.Tk()
    app = EncryptionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
