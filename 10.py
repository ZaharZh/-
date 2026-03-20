import math

def phi(x1, x2):
    u = x1**2 + 2*x1*x2 + 2*x2 + 0.5
    f1 = math.pi/2 - math.atan(u) - 0.2
    f2 = math.cos(0.1 * x2 ** 2 + x2 - 0.02 * x1 ** 2)
    return f1 ** 2 + f2 ** 2

def numerical_gradient(x1, x2, h=1e-8):
    grad_x1 = (phi(x1 + h, x2) - phi(x1 - h, x2)) / (2 * h)
    grad_x2 = (phi(x1, x2 + h) - phi(x1, x2 - h)) / (2 * h)
    return grad_x1, grad_x2

def gradient_descent_with_vector_diff(x1_0, x2_0, epsilon=1e-8, learning_rate=0.01, max_iter=10000):
    x1, x2 = x1_0, x2_0

    for i in range(1, max_iter + 1):
        grad_x1, grad_x2 = numerical_gradient(x1, x2)

        new_x1 = x1 - learning_rate * grad_x1
        new_x2 = x2 - learning_rate * grad_x2

        diff_norm = math.sqrt((new_x1 - x1) ** 2 + (new_x2 - x2) ** 2)

        if diff_norm < epsilon:
            final_x1, final_x2 = new_x1, new_x2
            final_grad = (grad_x1, grad_x2)
            final_phi = phi(final_x1, final_x2)
            return final_x1, final_x2, i, final_grad, final_phi

        x1, x2 = new_x1, new_x2

    final_grad = numerical_gradient(x1, x2)
    final_phi = phi(x1, x2)
    return x1, x2, max_iter, final_grad, final_phi

x1_start, x2_start = 0.0, 1.0
epsilon = 1e-8
learning_rate = 0.1

x1_sol, x2_sol, iters, grad_final, phi_final = gradient_descent_with_vector_diff(
    x1_start, x2_start,
    epsilon=epsilon,
    learning_rate=learning_rate,
    max_iter=20000
)

print(f"Решение x^(k) = ({x1_sol:.8f}, {x2_sol:.8f})")
print(f"Количество итераций k = {iters}")
print(f"Значение функции Φ(x^(k)) = {phi_final:.2e}")
print(f"Градиент ∇Φ(x^(k)) = ({grad_final[0]:.6e}, {grad_final[1]:.6e})")
print(f"Точность ε = {epsilon:.1e}")
