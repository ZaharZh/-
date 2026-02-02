import tkinter as tk
from tkinter import ttk

class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Шифрование текста")
        self.root.geometry("800x600")
        
        # Переменные
        self.key_var = tk.StringVar(value="3")
        
        # Создание виджетов
        self.create_widgets()
        
    def create_widgets(self):
        # Стиль
        style = ttk.Style()
        style.configure("TButton", padding=6, font=("Arial", 10))
        style.configure("TLabel", font=("Arial", 10))
        
        # Фрейм для исходного текста
        input_frame = ttk.LabelFrame(self.root, text="Исходный текст", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.input_text = tk.Text(input_frame, height=6, font=("Courier", 10))
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(control_frame, text="Ключ шифрования:").pack(side=tk.LEFT, padx=(0, 5))
        self.key_entry = ttk.Entry(control_frame, textvariable=self.key_var, width=10)
        self.key_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(control_frame, text="Зашифровать", command=self.encrypt).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Расшифровать", command=self.decrypt).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Очистить все", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Фрейм для зашифрованного текста
        encrypted_frame = ttk.LabelFrame(self.root, text="Зашифрованный текст", padding=10)
        encrypted_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.encrypted_text = tk.Text(encrypted_frame, height=6, font=("Courier", 10), bg="#f0f0f0")
        self.encrypted_text.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для расшифрованного текста
        decrypted_frame = ttk.LabelFrame(self.root, text="Расшифрованный текст", padding=10)
        decrypted_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        self.decrypted_text = tk.Text(decrypted_frame, height=6, font=("Courier", 10), bg="#f0f0f0")
        self.decrypted_text.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем скроллбары для текстовых полей
        for text_widget in [self.input_text, self.encrypted_text, self.decrypted_text]:
            scrollbar = ttk.Scrollbar(text_widget)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=text_widget.yview)
    
    def caesar_cipher(self, text, shift, mode='encrypt'):
        """Простой шифр Цезаря для демонстрации"""
        result = ""
        shift = int(shift)
        
        if mode == 'decrypt':
            shift = -shift
            
        for char in text:
            if char.isalpha():
                start = ord('а') if char.islower() else ord('А')
                result += chr((ord(char) - start + shift) % 32 + start)
            elif char.isdigit():
                result += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
            else:
                result += char
        return result
    
    def encrypt(self):
        """Шифрование текста"""
        try:
            text = self.input_text.get("1.0", tk.END).strip()
            key = self.key_var.get()
            
            if not text:
                return
                
            encrypted = self.caesar_cipher(text, key, 'encrypt')
            self.encrypted_text.delete("1.0", tk.END)
            self.encrypted_text.insert("1.0", encrypted)
            
        except ValueError:
            self.show_error("Ключ должен быть числом!")
    
    def decrypt(self):
        """Расшифрование текста"""
        try:
            text = self.encrypted_text.get("1.0", tk.END).strip()
            key = self.key_var.get()
            
            if not text:
                # Если в зашифрованном поле пусто, берем из исходного
                text = self.input_text.get("1.0", tk.END).strip()
                if not text:
                    return
            
            decrypted = self.caesar_cipher(text, key, 'decrypt')
            self.decrypted_text.delete("1.0", tk.END)
            self.decrypted_text.insert("1.0", decrypted)
            
        except ValueError:
            self.show_error("Ключ должен быть числом!")
    
    def clear_all(self):
        """Очистка всех полей"""
        self.input_text.delete("1.0", tk.END)
        self.encrypted_text.delete("1.0", tk.END)
        self.decrypted_text.delete("1.0", tk.END)
        self.key_var.set("3")
    
    def show_error(self, message):
        """Показать сообщение об ошибке"""
        error_window = tk.Toplevel(self.root)
        error_window.title("Ошибка")
        error_window.geometry("300x100")
        
        ttk.Label(error_window, text=message, wraplength=250).pack(pady=20)
        ttk.Button(error_window, text="OK", command=error_window.destroy).pack()

def main():
    root = tk.Tk()
    app = EncryptionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
