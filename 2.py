import numpy as np
import matplotlib.pyplot as plt

def f_scalar(x):
    return (x - 1.1) * np.sqrt(x + 3) * np.exp(-x ** 2) - x


def df_scalar(x):
    sqrt_term = np.sqrt(x + 3)
    exp_term = np.exp(-x ** 2)
    term1 = sqrt_term * exp_term
    term2 = (x - 1.1) * (1 / (2 * sqrt_term)) * exp_term
    term3 = (x - 1.1) * sqrt_term * (-2 * x) * exp_term
    return term1 + term2 + term3 - 1.0


f = np.vectorize(f_scalar)

def modified_newton(f_scalar, df_scalar, x0, tol=1e-4, max_iter=1000):
    df0 = df_scalar(x0)

    x = x0
    sequence = [x]

    for k in range(1, max_iter + 1):
        fx = f_scalar(x)

        if abs(fx) < tol:
            return x, k - 1, sequence

        x_new = x - fx / df0
        sequence.append(x_new)
        x = x_new

    return x, max_iter, sequence

x0 = -0.5
tol = 1e-4

root, n_iter, seq = modified_newton(f_scalar, df_scalar, x0, tol=tol, max_iter=1000)


print("Итерационная последовательность {x_k}:")
for i, xk in enumerate(seq):
    print(f"  x_{i:2d} = {xk:.8f}")


if root is not None:
    fx_root = f_scalar(root)
    print(f"\nНайденный корень:        x = {root:.8f}")
    print(f"Значение функции в корне: f(x) = {fx_root:.2e}")
    print(f"Количество итераций:     {n_iter}")
else:
    print("\nКорень не найден.")

xs = np.linspace(-2.9, 3, 10001)  # избегаем x = -3, но близко
ys = f(xs)

plt.figure(figsize=(10, 5))
plt.plot(xs, ys, label=r"$f(x) = (x - 1.1)\sqrt{x + 3}\,e^{-x^2} - x$", color='steelblue')
plt.axhline(0, color='black', linewidth=0.6)
plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)

if root is not None:
    plt.plot(root, f_scalar(root), 'go', markersize=8, label="Найденный корень")

plt.xlim(-2.9, 3)
plt.ylim(-3, 2)
plt.xlabel("x")
plt.ylabel("f(x)")
plt.title("Модифицированный метод Ньютона — график функции")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()