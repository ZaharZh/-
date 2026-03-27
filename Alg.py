import random


DINOSAURS = {
    "Микрораптор":    1,   "Анхиорнис":    2,   "Компсогнат":   3,
    "Зораптор":       4,   "Орадромус":    5,   "Агилизавр":    6,
    "Лейлинозавр":    7,   "Гетеродонтозавр": 8, "Игуанодон":    9,
    "Гадрозавр":     10,   "Пахицефалозавр": 15, "Ламбеозавр":  20,
    "Паразауролоф":  25,   "Трицератопс":  30,   "Стегозавр":   35,
    "Анкилозавр":    40,   "Спинозавр":    45,   "Капрозух":    50,
    "Кархародонтозавр": 55, "Гигантозавр": 60,   "Тираннозавр": 65,
    "Апатозавр":     70,   "Диплодок":     75,   "Брахиозавр":  80,
    "Велоцираптор":  85,   "Аллозавр":     90,   "Анкилозавр":  95,
    "Торозавр":     100,   "Паразауролоф": 110, "Стигимолох":  120,
    "Плеховик":     130,   "Нодозавр":    140,   "Эдмонтозавр": 150,
    "Майазавра":    160,   "Овираптор":   170,   "Дейноних":    180,
    "Ютараптор":    190,   "Акутилодон":  200,   "Сухомим":     220,
    "Галлимим":     240,   "Орнитомим":   260,   "Струтиомим":  280,
    "Дейнохейрус":  300,   "Теризинозавр": 350, "Секозавр":    400,
    "Аргентинозавр": 450, "Дредноут":    500,   "Патаготитан": 600,
    "Брахититан":   750,   "Диплодок":    900,
}

NAMES = list(DINOSAURS.keys())
POWER = list(DINOSAURS.values())
N = len(POWER)


POPULATION_SIZE = 200      
GENERATIONS = 5000         
CROSSOVER_RATE = 0.8       
MUTATION_RATE = 0.05      
ELITE_COUNT = 2           


def random_individual():
    return [random.randint(0, 1) for _ in range(N)]


def fitness(individual, target):
    total = sum(p * g for p, g in zip(POWER, individual))
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


def genetic_algorithm(target):
    population = [random_individual() for _ in range(POPULATION_SIZE)]

    for generation in range(1, GENERATIONS + 1):
        fitnesses = [fitness(ind, target) for ind in population]

        best_idx = min(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
        best_fit = fitnesses[best_idx]

        if generation % 500 == 0 or best_fit == 0:
            total = sum(p * g for p, g in zip(POWER, population[best_idx]))
            print(f"Поколение {generation:>5}: лучшая разница = {best_fit} ед. силы "
                  f"(суммарная сила = {total} ед.)")

        if best_fit == 0:
            print(">>> Найдено идеальное сочетание динозавров!")
            return population[best_idx], generation

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

    fitnesses = [fitness(ind, target) for ind in population]
    best_idx = min(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
    return population[best_idx], GENERATIONS


def print_result(individual, target):
    selected = [(NAMES[i], POWER[i]) for i in range(N) if individual[i] == 1]
    total = sum(power for _, power in selected)

    print("\n" + "=" * 60)
    print(f"Целевой уровень силы:  {target} ед.")
    print(f"Набранная сила отряда: {total} ед.")
    print(f"Разница:               {abs(total - target)} ед.")
    print(f"В отряде динозавров:   {len(selected)}")
    print("-" * 60)
    for name, power in selected:
        print(f"  {name:<20} — {power:>5} ед. силы")
    print("=" * 60)


def main():
    target = int(input("Введите целевой уровень силы отряда (ед.): "))
    print(f"\nЗапуск генетического алгоритма для подбора отряда с силой {target} ед.\n")

    best_individual, gen = genetic_algorithm(target)
    print_result(best_individual, target)
    print(f"Алгоритм завершился на поколении {gen}")


if __name__ == "__main__":
    main()