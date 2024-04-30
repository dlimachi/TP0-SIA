import sys
import numpy as np
import sympy as sp


class NonLinearPerceptron:

    def __init__(self, data_set, learning_rate, limit):
        self.data_set = data_set
        self.learning_rate = learning_rate
        self.limit = limit

        self.w_min = None
        self.min_val = None
        self.max_val = None
        self.normalized_data = self.normalize_data()

        self.x_symbol = sp.symbols('x')
        self.activation_function = sp.tanh(1.0 * self.x_symbol)
        self.activation_diff = sp.diff(self.activation_function, self.x_symbol)

    def initialize_weights(self, n):
        return np.random.rand(n)

    def compute_excitement(self, x, w):
        return w[0] + np.dot(x[1:], w[1:])

    def compute_error(self, data_with_bias, w):
        total_error = 0

        for x, expected in data_with_bias:
            h = self.compute_excitement(x, w)
            o = float(self.activation_function.subs(self.x_symbol, h).evalf())
            total_error += (expected - o) ** 2
        return total_error / 2  # MSE

    def perceptron_training(self, normalized_data):
        data_with_bias = [(np.array([1] + list(x)), y) for x, y in normalized_data]

        n = len(data_with_bias[0][0])  # Number of features
        w = self.initialize_weights(n)
        min_error = sys.maxsize
        w_min = None
        i = 0

        intermediate_weights = [w]
        while min_error > 0 and i < self.limit:
            mu = np.random.randint(len(data_with_bias))
            x_mu, zeta_mu = data_with_bias[mu]

            h_mu = self.compute_excitement(x_mu, w)
            o_mu = float(self.activation_function.subs(self.x_symbol, h_mu).evalf())

            delta_w = self.learning_rate * (zeta_mu - o_mu) * x_mu * float(
                self.activation_diff.subs(self.x_symbol, h_mu).evalf())
            w = w + delta_w

            error = self.compute_error(data_with_bias, w)
            if error < min_error:
                min_error = error
                w_min = w
                intermediate_weights.append(w_min)

            i += 1

        self.w_min = w_min

        return intermediate_weights, w_min

    def normalize_data(self):
        # Normalización de la segunda columna a [-1, 1]
        y_values = np.array([item[1] for item in self.data_set])
        self.min_val, self.max_val = y_values.min(), y_values.max()

        normalized_data = [(x, self.normalize_value(y)) for x, y in self.data_set]
        return normalized_data

    def normalize_value(self, x):
        """ Normaliza una entrada usando el mínimo y máximo utilizado en el entrenamiento. """
        return 2 * ((x - self.min_val) / (self.max_val - self.min_val)) - 1

    def denormalize_value(self, y_norm):
        """ Convierte una salida normalizada de vuelta a su escala original. """
        return (y_norm + 1) / 2 * (self.max_val - self.min_val) + self.min_val

    def run(self):
        return self.perceptron_training(self.normalized_data)

    def predict(self, x):
        if self.w_min is None:
            print("First you have to train the perceptron")
            return None
        else:
            # Agregamos un '1' para poder multiplicar w0*1 en el dot product.
            x_with_bias = np.insert(x, 0, 1)
            h = self.compute_excitement(x_with_bias, self.w_min)
            return self.denormalize_value(h)
