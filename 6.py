import numpy as np
import matplotlib.pyplot as plt

def gauss_solve(A, b):
    A = [row[:] for row in A]
    b = b[:]
    n = len(b)
    
    for i in range(n):
        max_row = max(range(i, n), key=lambda r: abs(A[r][i]))
        
        if abs(A[max_row][i]) < 1e-12:
            raise ValueError("Матрица вырождена")
        
        A[i], A[max_row] = A[max_row], A[i]
        b[i], b[max_row] = b[max_row], b[i]
        
        currI = A[i][i]
        
        for j in range(i, n):
            A[i][j] /= currI
        b[i] /= currI
        
        for k in range(i+1, n):
            f = A[k][i]
            for j in range(i, n):
                A[k][j] -= f * A[i][j]
            b[k] -= f * b[i]
    
    x = [0] * n
    for i in range(n-1, -1, -1):
        x[i] = b[i] - sum(A[i][j] * x[j] for j in range(i+1, n))
    
    return x

def f(x):
    return (x - 1.1) * np.sqrt(x + 3) * np.exp(-x ** 2) - x

def solve_normal_equations(x, y, degree):

    A = np.zeros((degree + 1, degree + 1))
    
    b = np.zeros(degree + 1)

    for i in range(degree + 1):
        for j in range(degree + 1):
            A[i, j] = np.sum(x ** (i + j))
        b[i] = np.sum(y * (x ** i))

    try:
        coeffs = gauss_solve(A.tolist(), b.tolist())
    except ValueError:
        raise ValueError("Матрица вырождена")
    return coeffs

def evaluate_poly(coeffs, x):
    result = np.zeros_like(x, dtype=float)
    for i, a in enumerate(coeffs):
        result += a * (x ** i)
    return result

n_points = 50

x_min, x_max = 0, 10

x_data = np.linspace(x_min, x_max, n_points)

y_clean = f(x_data)
rel_err = np.random.uniform(0.3, 3.0, size=n_points)

sign = np.random.choice([-1, 1], size=n_points)

noise = sign * rel_err * np.abs(y_clean)

for i in range(len(y_clean)):
    if np.abs(y_clean[i]) < 1e-8:
        noise[i] = np.random.uniform(-1, 1)

y_noisy = y_clean + noise

degrees = list(range(1, 6))
results = []
y_mean = np.mean(y_noisy)

ss_total = np.sum((y_noisy - y_mean) ** 2)

x_plot = np.linspace(x_min, x_max, 10001)
y_true_plot = f(x_plot)

plt.figure(figsize=(14, 9))
plt.scatter(x_data, y_noisy, color='red', s=40, zorder=10, label='Зашумлённые данные')
plt.plot(x_plot, y_true_plot, 'k--', linewidth=2.5, label='Истинная функция')

for idx, deg in enumerate(degrees):
    coeffs = solve_normal_equations(x_data, y_noisy, deg)
    y_pred_plot = evaluate_poly(coeffs, x_plot)
    y_pred_train = evaluate_poly(coeffs, x_data)

    rmse = np.sqrt(np.mean((y_noisy - y_pred_train) ** 2))
    ss_res = np.sum((y_noisy - y_pred_train) ** 2)
    r2 = 1 - (ss_res / ss_total) if ss_total > 1e-12 else 0.0

    results.append({
        'degree': deg,
        'rmse': rmse,
        'r2': r2,
        'coeffs': coeffs
    })

    plt.plot(x_plot, y_pred_plot, linewidth=2,
             label=f'Полином степени {deg} (RMSE={rmse:.3f})')

plt.xlabel('x', fontsize=12)
plt.ylabel('y', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

best = min(results, key=lambda r: r['rmse'])

for r in results:
    print(f"Полином степени {r['degree']:1d}: RMSE = {r['rmse']:.4f}, R² = {r['r2']:.4f}")

print(f"Наилучшая модель: полином степени {best['degree']}")
print(f"Минимальный RMSE = {best['rmse']:.4f}")
