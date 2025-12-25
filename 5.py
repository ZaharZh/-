import pandas as pd

def zeros(n):
    return [0.0] * n

def max_abs_diff(a, b):
    return max(abs(a[i] - b[i]) for i in range(len(a)))

def dot_row_vector(row, x):
    return sum(row[j] * x[j] for j in range(len(x)))

def jacobi_solve(A, b, eps=1e-4, max_iter=10000):
    n = len(b)
    x_old = zeros(n)
    x_new = zeros(n)

    for iteration in range(1, max_iter + 1):
        for i in range(n):
            s = 0.0
            for j in range(n):
                if j != i:
                    s += A[i][j] * x_old[j]
            x_new[i] = (b[i] - s) / A[i][i]

        diff = max_abs_diff(x_new, x_old)
        if diff < eps:
            return x_new, iteration

        x_old = x_new[:]

    raise RuntimeError(f"Метод Якоби не сошёлся за {max_iter} итераций.")

def compute_residual(A, b, x):
    n = len(b)
    residual = zeros(n)
    for i in range(n):
        Ax_i = dot_row_vector(A[i], x)
        residual[i] = b[i] - Ax_i
    return residual


data = pd.read_csv('4.csv')

A = []
b = []
for idx in range(4):
    row = [
        float(data.iloc[idx]['x1']),
        float(data.iloc[idx]['x2']),
        float(data.iloc[idx]['x3']),
        float(data.iloc[idx]['x4'])
    ]
    A.append(row)
    b.append(float(data.iloc[idx]['y']))


x, iters = jacobi_solve(A, b, eps=1e-4)
residual = compute_residual(A, b, x)

print("Решение (вектор x):")
for i in range(4):
    print(f"x{i+1} = {x[i]:.6f}")

print("\nНевязка (r = b - A·x):")
for i in range(4):
    print(f"r{i+1} = {residual[i]:.2e}")

print(f"\nЧисло итераций: {iters}")


