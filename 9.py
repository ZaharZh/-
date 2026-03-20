import math

def f1(x1, x2):
    u = x1**2 + 2*x1*x2 + 2*x2 + 0.5
    return math.pi/2 - math.atan(u) - 0.2

def f2(x1, x2):
    return math.cos(0.1*x2**2 + x2 - 0.02*x1**2)

def jacobian(x1, x2):
    u = x1**2 + 2*x1*x2 + 2*x2 + 0.5
    denom = 1.0 + u**2
    df1_dx1 = -(2*x1 + 2*x2) / denom
    df1_dx2 = -(2*x1 + 2) / denom

    v = 0.1*x2**2 + x2 - 0.02*x1**2
    sin_v = math.sin(v)
    df2_dx1 = 0.04*x1 * sin_v
    df2_dx2 = -(0.2*x2 + 1.0) * sin_v

    return [[df1_dx1, df1_dx2],
            [df2_dx1, df2_dx2]]

def solve_2x2(A, b):
    a11, a12 = A[0]
    a21, a22 = A[1]
    det = a11 * a22 - a12 * a21
    if abs(det) < 1e-12:
        raise ValueError("Якобиан вырожден на данной итерации.")
    dx1 = (b[0] * a22 - b[1] * a12) / det
    dx2 = (a11 * b[1] - a21 * b[0]) / det
    return [dx1, dx2]

def modified_newton(x1_0, x2_0, tol=1e-8, max_iter=100):
    x1, x2 = x1_0, x2_0

    J_fixed = jacobian(x1_0, x2_0)

    for k in range(max_iter):
        F1 = f1(x1, x2)
        F2 = f2(x1, x2)
        F_norm = math.sqrt(F1**2 + F2**2)

        print(f"Итерация {k}: x1 = {x1:.10f}, x2 = {x2:.10f}, ||F|| = {F_norm:.2e}")

        if F_norm < tol:
            print("Сходимость достигнута.")
            return x1, x2

        dx = solve_2x2(J_fixed, [-F1, -F2])

        x1 += dx[0]
        x2 += dx[1]

        if abs(dx[0]) < tol and abs(dx[1]) < tol:
            print("Приращение слишком мало")
            break

    print("Достигнуто максимальное число итераций.")
    return x1, x2


x1_sol, x2_sol = modified_newton(-0.77, -1.9)
print("\nРешение:")
print(f"x1 = {x1_sol:.10f}")
print(f"x2 = {x2_sol:.10f}")
print(f"f1 = {f1(x1_sol, x2_sol):.2e}")
print(f"f2 = {f2(x1_sol, x2_sol):.2e}")
