import numpy as np
from scipy import integrate

def trapezoidal_manual(f, a, b, N):
    if N < 2:
        raise ValueError("N должно быть не меньше 2.")
    h = (b - a) / (N - 1)
    x = np.linspace(a, b, N)
    y = f(x)
    integral = h * (0.5 * y[0] + np.sum(y[1:-1]) + 0.5 * y[-1])
    return integral

def f(x):
    return (x - 1.1) * np.sqrt(x + 3) * np.exp(-x**2) - x

a, b = 3, 6
eps = 1e-4

N = 2
T_prev = trapezoidal_manual(f, a, b, N)
N *= 2
iteration = 1

print(f"Интегрирование методом трапеций с точностью {eps}")
print(f"{'Итерация':>9} {'N':>8} {'T_N':>14} {'|ΔT|':>12}")
print("-" * 42)

while True:
    T_curr = trapezoidal_manual(f, a, b, N)
    diff = abs(T_curr - T_prev)
    print(f"{iteration:9d} {N:8d} {T_curr:14.10f} {diff:12.2e}")
    
    if diff < eps:
        break
        
    T_prev = T_curr
    N *= 2
    iteration += 1

I_exact, _ = integrate.quad(f, a, b)
error_vs_exact = abs(T_curr - I_exact)

print("\nРезультат:")
print(f"Приближённое значение интеграла: {T_curr:.10f}")
print(f"Достигнута точность по |T_N - T_N/2| < {eps}")
print(f"Фактическая ошибка (vs scipy.quad): {error_vs_exact:.2e}")