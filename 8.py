import math
import matplotlib.pyplot as plt

def f(x, y):
    if x - y**2 <= 0:
        raise ValueError(f"Недопустимое значение: x - y^2 = {x - y**2} <= 0 при x={x}, y={y}")
    return math.log(x - y**2) - math.tan(y - x)

def euler_coshi(f, x0, y0, b, h):
    x_list = []
    y_list = []

    x = x0
    y = y0

    while x <= b + 1e-12:
        x_list.append(x)
        y_list.append(y)

        k1 = f(x, y)
        y_pred = y + h * k1

        k2 = f(x + h, y_pred)
        y = y + (h / 2) * (k1 + k2)

        x += h

    return x_list, y_list

x0 = 1.0
y0 = 0.0
a = 1.0
b = 2.0
h = 0.01

try:
    x_vals, y_vals = euler_coshi(f, x0, y0, b, h)
except ValueError as e:
    print("Ошибка при решении ОДУ:", e)
    exit()

check_points = [1.0, 1.5, 2.0]

print("Сравнение численной производной и правой части ОДУ:")
for x_check in check_points:
    idx = min(range(len(x_vals)), key=lambda i: abs(x_vals[i] - x_check))
    x_approx = x_vals[idx]
    y_approx = y_vals[idx]

    if 0 < idx < len(x_vals) - 1:
        dy_dx_num = (y_vals[idx + 1] - y_vals[idx - 1]) / (2 * h)
    elif idx == 0:
        dy_dx_num = (y_vals[1] - y_vals[0]) / h
    else:
        dy_dx_num = (y_vals[-1] - y_vals[-2]) / h

    try:
        f_analytic = f(x_approx, y_approx)
    except ValueError as e:
        f_analytic = float('nan')
        print(f"  Невозможно вычислить f({x_approx:.3f}, {y_approx:.3f})")

    error = abs(dy_dx_num - f_analytic) if not math.isnan(f_analytic) else float('nan')

    print(f"\nx = {x_check:.3f}")
    print(f"  Численная производная:          {dy_dx_num:.8f}")
    print(f"  Аналитическая f(x,y):           {f_analytic:.8f}")
    print(f"  Погрешность:                    {error:.8f}")

plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals, 'b-', linewidth=2, label='Решение (Эйлер–Коши)')
plt.scatter([x0], [y0], color='red', s=80, zorder=5, label='Начальное условие y(1)=0')
plt.title('Решение ОДУ: $y\' = \\ln(x - y^2) - \\tan(y - x)$, $y(1) = 0$')
plt.xlabel('x')
plt.ylabel('y(x)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.xlim(a, b)
plt.ylim(min(y_vals) - 0.1, max(y_vals) + 0.1)
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(1, color='gray', linestyle=':', linewidth=1)  # начальная точка по x
plt.show()