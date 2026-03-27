import random
import threading
import tkinter as tk
from tkinter import scrolledtext

# ---------- Данные о заболеваниях ----------
DISEASES = {
    "Острый ринит": 1,
    "Аллергический ринит": 2,
    "Хронический ринит": 3,
    "Острый синусит": 4,
    "Хронический синусит": 5,
    "Полипоз носа": 6,
    "Искривление носовой перегородки": 7,
    "Острый фарингит": 8,
    "Хронический фарингит": 9,
    "Острый тонзиллит (ангина)": 10,
    "Хронический тонзиллит": 15,
    "Паратонзиллярный абсцесс": 20,
    "Острый ларингит": 25,
    "Хронический ларингит": 30,
    "Узелки голосовых складок": 35,
    "Острый отит": 40,
    "Хронический отит": 45,
    "Экссудативный отит": 50,
    "Отосклероз": 55,
    "Болезнь Меньера": 60,
    "Доброкачественное пароксизмальное позиционное головокружение": 65,
    "Лабиринтит": 70,
    "Невринома слухового нерва": 75,
    "Тугоухость нейросенсорная": 80,
    "Тугоухость кондуктивная": 85,
    "Аденоиды": 90,
    "Стеноз гортани": 95,
    "Папилломатоз гортани": 100,
    "Рак гортани": 110,
    "Рак носоглотки": 120,
    "Рак околоносовых пазух": 130,
    "Гранулематоз Вегенера": 140,
    "Саркоидоз ЛОР-органов": 150,
    "Туберкулёз гортани": 160,
    "Сифилис ЛОР-органов": 170,
    "Инородное тело носа": 180,
    "Инородное тело уха": 190,
    "Инородное тело глотки": 200,
    "Перфорация барабанной перепонки": 220,
    "Холестеатома": 240,
    "Отогенный менингит": 260,
    "Абсцесс мозга": 280,
    "Сепсис ЛОР-происхождения": 300,
    "Ангионевротический отёк гортани": 350,
    "Ларингоспазм": 400,
    "Острая дыхательная недостаточность": 450,
    "Хроническая дыхательная недостаточность": 500,
    "Трахеостома": 600,
    "Ларингэктомия": 750,
    "Кохлеарная имплантация": 900,
}

NAMES = list(DISEASES.keys())
SEVERITY = list(DISEASES.values())
N = len(SEVERITY)

# Параметры алгоритма
POPULATION_SIZE = 200
GENERATIONS = 5000
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.05
ELITE_COUNT = 2


# ---------- Функции генетического алгоритма ----------
def random_individual():
    return [random.randint(0, 1) for _ in range(N)]


def fitness(individual, target):
    total = sum(s * g for s, g in zip(SEVERITY, individual))
    return abs(total - target)


def tournament_selection(population, fitnesses, k=3):
    candidates = random.sample(range(len(population)), k)
    best = min(candidates, key=lambda i: fitnesses[i])
    return population[best][:]


def crossover(parent1, parent2):
    if random.random() > CROSSOVER_RATE:
        return parent1[:], parent2[:]
    point = random.randint(1, N - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def mutate(individual):
    for i in range(N):
        if random.random() < MUTATION_RATE:
            individual[i] = 1 - individual[i]


def genetic_algorithm(target, report_callback=None):
    """
    Запуск генетического алгоритма.
    Если передан report_callback, он вызывается с текстовыми сообщениями.
    Возвращает (лучшая_особь, номер_поколения_остановки).
    """
    population = [random_individual() for _ in range(POPULATION_SIZE)]

    for generation in range(1, GENERATIONS + 1):
        fitnesses = [fitness(ind, target) for ind in population]
        best_idx = min(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
        best_fit = fitnesses[best_idx]

        if generation % 500 == 0 or best_fit == 0:
            total = sum(s * g for s, g in zip(SEVERITY, population[best_idx]))
            msg = f"Поколение {generation:>5}: разница = {best_fit} ед. тяжести (сумма = {total} ед.)"
            if report_callback:
                report_callback(msg)
            else:
                print(msg)

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
        self.title("Подбор ЛОР-заболеваний")
        self.geometry("700x500")

        # Поле ввода
        tk.Label(self, text="Целевая тяжесть (ед.):").pack(pady=5)
        self.target_entry = tk.Entry(self)
        self.target_entry.pack(pady=5)
        self.target_entry.insert(0, "500")

        # Кнопка запуска
        self.start_button = tk.Button(self, text="Подобрать", command=self.start_search)
        self.start_button.pack(pady=5)

        # Текстовое поле для вывода
        self.output = scrolledtext.ScrolledText(self, wrap=tk.WORD, state='normal')
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.output.config(state='disabled')

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

        self.output.config(state='normal')
        self.output.delete(1.0, tk.END)
        self.output.config(state='disabled')
        self.log(f"Запуск подбора для целевой тяжести {target} ед.\n")

        # Запускаем поток
        self.search_thread = threading.Thread(target=self.run_algorithm, args=(target,))
        self.search_thread.daemon = True
        self.search_thread.start()

    def run_algorithm(self, target):
        """Выполняет алгоритм и выводит результат."""
        # Передаём callback для вывода сообщений
        best, last_gen = genetic_algorithm(target, report_callback=self.log)

        # Построение итогового вывода
        selected = [(NAMES[i], SEVERITY[i]) for i in range(N) if best[i] == 1]
        total = sum(sev for _, sev in selected)

        self.log("\n" + "=" * 60)
        self.log(f"Целевой уровень тяжести:      {target} ед.")
        self.log(f"Суммарная тяжесть набора:     {total} ед.")
        self.log(f"Разница (отклонение):         {abs(total - target)} ед.")
        self.log(f"Количество заболеваний:       {len(selected)}")
        self.log("-" * 60)
        for name, sev in selected:
            self.log(f"  {name:<35} — {sev:>5} ед. тяжести")
        self.log("=" * 60)
        self.log(f"Алгоритм завершён на поколении {last_gen}")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
