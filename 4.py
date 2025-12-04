import pandas as pd
import numpy as np

def inverse_via_gauss_pivoting(A):

    A = np.array(A, dtype=float)
    n = A.shape[0]

    aug = np.concatenate((A.copy(), np.eye(n)), axis=1)

    for k in range(n):
        max_idx = k + np.argmax(np.abs(aug[k:, k]))

        if np.abs(aug[max_idx, k]) < 1e-12:
            raise ValueError("Матрица вырождена. Обратная матрица не существует.")

        if max_idx != k:
            aug[[k, max_idx]] = aug[[max_idx, k]]

        for i in range(k + 1, n):
            factor = aug[i, k] / aug[k, k]
            aug[i, k:] -= factor * aug[k, k:]

    for k in range(n - 1, -1, -1):
        aug[k, k:] /= aug[k, k]
        for i in range(k):
            factor = aug[i, k]
            aug[i, k:] -= factor * aug[k, k:]

    return aug[:, n:]

filename = "4.csv"


data = pd.read_csv(filename)
A = data.values

print("Исходная матрица A:")
print(A)
print()

A_inv = inverse_via_gauss_pivoting(A)

print("Обратная матрица A⁻¹:")
print(A_inv)
print()

product = A @ A_inv

print("Результат произведения A @ A⁻¹ (должен быть ≈ I):")
print(np.round(product, decimals=10))
