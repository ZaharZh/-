import tkinter as tk
from tkinter import scrolledtext, messagebox
import hashlib

# ---------- MD5 функция ----------
def compute_md5(text: str) -> str:
    """Вычисляет MD5-хеш от переданной строки и возвращает его в шестнадцатеричном виде."""
    # Преобразуем строку в байты (используем UTF-8) и вычисляем хеш
    hash_object = hashlib.md5(text.encode('utf-8'))
    return hash_object.hexdigest()

# ---------- GUI ----------
class MD5App:
    def __init__(self, root):
        self.root = root
        self.root.title("MD5 Хеширование")
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
