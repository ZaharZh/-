import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def f_scalar(x):
    return (x - 1.1) * np.sqrt(x + 3) * np.exp(-x ** 2) - x

f = np.vectorize(f_scalar)

def parabolic_method(f, x0, x1, x2, tol=1e-4, max_iter=100):

    sequence = [x1]

    for k in range(max_iter):
        f0, f1, f2 = f(x0), f(x1), f(x2)

        if (x1 - x0) == 0 or (x2 - x1) == 0:
            break

        a1 = (f1 - f0) / (x1 - x0)
        a2 = (f2 - f1) / (x2 - x1)

        if (x2 - x0) == 0:
            break
        b = (a2 - a1) / (x2 - x0)

        if abs(b) < 1e-14:
            break

        x_new = (x0 + x1) / 2.0 - a1 / (2.0 * b)

        f_new = f(x_new)
        sequence.append(x_new)

        if len(sequence) >= 2:
            if abs(sequence[-1] - sequence[-2]) < tol:
                candidates = [(x0, f0), (x1, f1), (x2, f2), (x_new, f_new)]
                best_x, best_f = min(candidates, key=lambda t: t[1])
                return best_x, best_f, k + 1, sequence

        points = sorted([(x0, f0), (x1, f1), (x2, f2), (x_new, f_new)], key=lambda t: t[0])
        updated = False
        for i in range(1, len(points) - 1):
            if points[i][1] <= points[i - 1][1] and points[i][1] <= points[i + 1][1]:
                x0, f0 = points[i - 1][0], points[i - 1][1]
                x1, f1 = points[i][0], points[i][1]
                x2, f2 = points[i + 1][0], points[i + 1][1]
                updated = True
                break
        if not updated:
            points_sorted_by_f = sorted(points, key=lambda t: t[1])
            triple = sorted(points_sorted_by_f[:3], key=lambda t: t[0])
            if len(triple) == 3:
                (x0, _), (x1, _), (x2, _) = triple
            else:
                break

    candidates = [(x0, f(x0)), (x1, f(x1)), (x2, f(x2))]
    best_x, best_f = min(candidates, key=lambda t: t[1])
    return best_x, best_f, max_iter, sequence

x0_init, x1_init, x2_init = -1, 0, 1
tol = 1e-4

xmin, fmin, n_iter, seq = parabolic_method(f_scalar, x0_init, x1_init, x2_init, tol=tol, max_iter=100)

print("Итерационная последовательность {x_k}:")
for i, xk in enumerate(seq):
    print(f"  x_{i:2d} = {xk:.8f}")


if xmin is not None:

    x = sp.symbols('x')
    ff = (x - 1.1) * (x + 3) ** 0.5 * np.e ** (-x ** 2) - x

    f_prime = sp.diff(ff, x)
    df_val = f_prime.subs(x, xmin)

    f_double_prime = sp.diff(f_prime, x)
    d2f_val = f_double_prime.subs(x, xmin)

    if d2f_val > 0:
        extremum_type = "локальный минимум"
    elif d2f_val < 0:
        extremum_type = "локальный максимум"
    else:
        extremum_type = "точка перегиба (требуется дополнительный анализ)"

    print(f"\nНайденная точка экстремума:  x = {xmin:.8f}")
    print(f"Значение функции в точке:     f(x) = {fmin:.8f}")
    print(f"Тип экстремума:               {extremum_type}")
    print(f"Первая производная f'(x):     {df_val:.2e}")
    print(f"Вторая производная f''(x):    {d2f_val:.4f}")
    print(f"Количество итераций:          {n_iter}")
else:
    print("\nЭкстремум не найден.")

xs = np.linspace(-2, 10, 10001)
ys = f(xs)

plt.figure(figsize=(10, 5))
plt.plot(xs, ys, label=r"$f(x) = (x - 1.1)\sqrt{x + 3}\,e^{-x^2} - x$", color='steelblue')
plt.axhline(0, color='black', linewidth=0.6)
plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)

if xmin is not None:
    plt.plot(xmin, fmin, 'ro', markersize=8, label="Найденный экстремум")

plt.ylim(-3, 2)
plt.xlabel("x")
plt.ylabel("f(x)")
plt.title("Метод парабол — поиск экстремума")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()