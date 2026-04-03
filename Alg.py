import random
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

# ---------- Параметры генетического алгоритма ----------
POPULATION_SIZE = 200
GENERATIONS = 5000
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.05
ELITE_COUNT = 2

# ---------- Данные о медицинских товарах (50 шт.) ----------
product_names = [
    "Бинт стерильный", "Марля медицинская", "Перчатки медицинские", "Маска защитная",
    "Антисептик", "Салфетки спиртовые", "Вата", "Пластырь", "Шприц одноразовый",
    "Капельница", "Термометр", "Тонометр", "Пульсоксиметр", "Глюкометр", "Тест-полоски",
    "Ингалятор", "Небулайзер", "Аспиратор", "Грелка", "Компресс", "Ортез", "Эластичный бинт",
    "Тейп", "Ножницы медицинские", "Пинцет", "Зеркало для осмотра", "Фонарик диагностический",
    "Шпатель", "Катетер", "Трубка", "Система для переливания", "Бахилы", "Колпак", "Халат",
    "Маска-респиратор", "Очки защитные", "Фартук", "Простыня", "Пеленка", "Подгузник",
    "Салфетка", "Жгут", "Лейкопластырь", "Крем", "Мазь", "Гель", "Спрей", "Капли", "Таблетки", "Сироп"
]
# Гарантируем ровно 50 товаров
product_names = product_names[:50]

N = 50  # количество товаров

# Генерация цен (руб.) и допустимых количеств
random.seed(42)  # для воспроизводимости
prices = [random.randint(50, 5000) for _ in range(N)]
min_qty = [1] * N               # минимальное количество = 1 (не может быть 0)
max_qty = [random.randint(5, 20) for _ in range(N)]

# Минимальная и максимальная общая стоимость (сумма всех товаров)
min_total = sum(prices[i] * min_qty[i] for i in range(N))
max_total = sum(prices[i] * max_qty[i] for i in range(N))

# ---------- Функции генетического алгоритма ----------
def random_individual():
    """Создаёт случайный набор количеств товаров в допустимых границах."""
    return [random.randint(min_qty[i], max_qty[i]) for i in range(N)]


def fitness(individual, target):
    """Разница между общей стоимостью и целевой суммой."""
    total = sum(prices[i] * individual[i] for i in range(N))
    return abs(total - target)


def tournament_selection(population, fitnesses, k=3):
    candidates = random.sample(range(len(population)), k)
    best = min(candidates, key=lambda i: fitnesses[i])
    return population[best][:]


def crossover(parent1, parent2):
    """Одноточечный кроссовер для списков целых чисел."""
    if random.random() > CROSSOVER_RATE:
        return parent1[:], parent2[:]
    point = random.randint(1, N - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def mutate(individual):
    """Мутация: с вероятностью MUTATION_RATE изменяем количество товара
    на случайную величину в пределах [-2, 2] с учётом границ."""
    for i in range(N):
        if random.random() < MUTATION_RATE:
            delta = random.randint(-2, 2)
            new_val = individual[i] + delta
            new_val = max(min_qty[i], min(max_qty[i], new_val))
            individual[i] = new_val


def genetic_algorithm(target, report_callback=None):
    """
    Запуск генетического алгоритма.
    Возвращает (лучшая_особь, номер_поколения_остановки).
    """
    population = [random_individual() for _ in range(POPULATION_SIZE)]

    for generation in range(1, GENERATIONS + 1):
        fitnesses = [fitness(ind, target) for ind in population]
        best_idx = min(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
        best_fit = fitnesses[best_idx]

        if generation % 500 == 0 or best_fit == 0:
            total = sum(prices[i] * population[best_idx][i] for i in range(N))
            msg = f"Поколение {generation:>5}: разница = {best_fit} руб. (сумма = {total} руб.)"
            if report_callback:
                report_callback(msg)

        if best_fit == 0:
            if report_callback:
                report_callback(">>> Найдено точное совпадение!")
            return population[best_idx], generation

        # Элитизм
        sorted_indices = sorted(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
        new_population = [population[i][:] for i in sorted_indices[:ELITE_COUNT]]

        while len(new_population) < POPULATION_SIZE:
            p1 = tournament_selection(population, fitnesses)
            p2 = tournament_selection(population, fitnesses)
            c1, c2 = crossover(p1, p2)
            mutate(c1)
            mutate(c2)
            new_population.append(c1)
            if len(new_population) < POPULATION_SIZE:
                new_population.append(c2)

        population = new_population

    # По окончании поколений
    fitnesses = [fitness(ind, target) for ind in population]
    best_idx = min(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
    return population[best_idx], GENERATIONS


# ---------- GUI ----------
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Подбор медицинских товаров по сумме")
        self.geometry("1000x700")

        # Фрейм для таблицы товаров
        table_frame = ttk.LabelFrame(self, text="Список медицинских товаров", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

        # Таблица (Treeview)
        columns = ("Название", "Цена (руб.)", "Мин. кол-во", "Макс. кол-во")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Заполнение таблицы
        for i in range(N):
            self.tree.insert("", tk.END, values=(
                product_names[i], prices[i], min_qty[i], max_qty[i]
            ))

        # Информация о ценах (минимальная и максимальная общая стоимость)
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text=f"Минимальная общая стоимость (все товары × мин. кол-во): {min_total} руб.").pack(side=tk.LEFT, padx=10)
        ttk.Label(info_frame, text=f"Максимальная общая стоимость (все товары × макс. кол-во): {max_total} руб.").pack(side=tk.LEFT, padx=10)

        # Поле ввода и кнопка
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(control_frame, text="Целевая сумма (руб.):").pack(side=tk.LEFT)
        self.target_entry = ttk.Entry(control_frame, width=15)
        self.target_entry.pack(side=tk.LEFT, padx=5)
        self.target_entry.insert(0, "5000")
        self.start_button = ttk.Button(control_frame, text="Подобрать", command=self.start_search)
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Текстовое поле для вывода хода алгоритма
        output_frame = ttk.LabelFrame(self, text="Результаты подбора", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.output = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, state='normal')
        self.output.pack(fill=tk.BOTH, expand=True)

        # Переменная для потока
        self.search_thread = None

    def log(self, message):
        """Добавление сообщения в текстовое поле (из любого потока)."""
        self.after(0, self._log_safe, message)

    def _log_safe(self, message):
        self.output.config(state='normal')
        self.output.insert(tk.END, message + "\n")
        self.output.see(tk.END)
        self.output.config(state='disabled')

    def start_search(self):
        """Запуск алгоритма в отдельном потоке."""
        if self.search_thread and self.search_thread.is_alive():
            self.log("Поиск уже выполняется, подождите...")
            return

        try:
            target = int(self.target_entry.get())
        except ValueError:
            self.log("Ошибка: введите целое число.")
            return

        # Проверка, находится ли целевая сумма в диапазоне возможных общих стоимостей
        if target < min_total:
            self.log(f"Внимание: целевая сумма {target} руб. меньше минимально возможной ({min_total} руб.).")
        if target > max_total:
            self.log(f"Внимание: целевая сумма {target} руб. больше максимально возможной ({max_total} руб.).")

        self.output.config(state='normal')
        self.output.delete(1.0, tk.END)
        self.output.config(state='disabled')
        self.log(f"Запуск подбора для целевой суммы {target} руб.\n")

        # Запускаем поток
        self.search_thread = threading.Thread(target=self.run_algorithm, args=(target,))
        self.search_thread.daemon = True
        self.search_thread.start()

    def run_algorithm(self, target):
        """Выполняет алгоритм и выводит результат."""
        best, last_gen = genetic_algorithm(target, report_callback=self.log)

        # Построение итогового вывода
        selected = [(product_names[i], prices[i], best[i]) for i in range(N) if best[i] > 0]
        total = sum(prices[i] * best[i] for i in range(N))

        self.log("\n" + "=" * 70)
        self.log(f"Целевая сумма:                {target} руб.")
        self.log(f"Общая стоимость набора:       {total} руб.")
        self.log(f"Разница (отклонение):         {abs(total - target)} руб.")
        self.log(f"Количество выбранных товаров: {len(selected)} (всего единиц: {sum(qty for _, _, qty in selected)})")
        self.log("-" * 70)
        for name, price, qty in selected:
            self.log(f"  {name:<35} — {qty:>3} шт. × {price:>5} руб. = {qty*price:>7} руб.")
        self.log("=" * 70)
        self.log(f"Алгоритм завершён на поколении {last_gen}")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
