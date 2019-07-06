import numpy as np
import logging


class LogisticRegression:

    def __init__(self, X_train, y_train, lamd, eps, max_iterations=500):
        """
                Initializes and creates a instance of l2 regularised logistic regression

                :param X_train: training features of shape (d, n)
                :param y_train: training labels of shape (d, 1)
                :param lamd: regularization parameter, default value 0.1
                :param eps: minimum slope to stop gradient descent, default - 0.001
                :param max_iterations: maximum number if iteration - default 1000. If minimum gradient is not
                                 is not reached in max iteration, the algorithm will stop optimizing further
                :param backtracking_max_iter: maximum number of iterations to optimize learning rate using
                                              backtracking line search
                """

        self.X_train = X_train
        self.y_train = y_train
        self.lamd = lamd
        self.max_iterations = max_iterations
        self.eps = eps
        self.d_train, self.n_train = self.X_train.shape

    def train(self):
        self.init_learning_rate = self.__compute_init_learning_rate__()
        self.beta, self.cost_history_fastgrad, self.beta_history = self.fast_grad_descent()

    def obj(self, beta):
        a = np.exp(self.y_train * (self.X_train.T.dot(beta)))
        b = np.sum(np.log(1 + a))
        residuals = self.lamd * np.square(np.linalg.norm(beta))
        cost = (b / self.n_train + residuals)
        return cost.squeeze()

    def compute_grad(self, beta):
        x = self.y_train * (self.X_train.T.dot(beta))
        a = (1 / (1 + np.exp(x)))
        p = np.diag(np.array(a).reshape(self.n_train, ))
        grad = -1 / self.n_train * (self.X_train.dot(p).dot(self.y_train)) + 2 * self.lamd * beta
        return grad

    def __compute_init_learning_rate__(self):
        eigenvalues, eigenvectors = np.linalg.eigh(1 / self.n_train * self.X_train.T.dot(self.X_train))
        lipschitz = max(eigenvalues) + self.lamd
        return 1 / lipschitz

    def bt_line_search(self, beta, alpha=0.5, gamma=0.8, max_iter=100):
        learning_rate = self.init_learning_rate
        grad = self.compute_grad(beta)
        z = beta - learning_rate * grad
        lhs = self.obj(z)
        rhs = self.obj(beta) - alpha * learning_rate * np.square(np.linalg.norm(grad))
        i = 0
        while rhs < lhs and i < max_iter:
            learning_rate *= gamma
            z = beta - learning_rate * grad
            lhs = self.obj(z)
            rhs = self.obj(beta) - alpha * learning_rate * np.square(np.linalg.norm(grad))
            i += 1
        return learning_rate

    def fast_grad_descent(self):

        beta = np.zeros((self.d_train, 1))
        theta = np.zeros((self.d_train, 1))
        cost_history_fastgrad = []
        beta_history = np.array(beta)

        for it in range(self.max_iterations):
            theta_grad = self.compute_grad(theta)
            error = np.linalg.norm(theta_grad)
            if error > self.eps:
                cost_history_fastgrad.append(self.obj(beta))
                t = self.bt_line_search(beta)
                beta = theta - (t * theta_grad)
                theta = beta + it / (it + 3) * (beta - beta_history[:, (it)].reshape(self.d_train, 1))
                beta_history = np.append(beta_history, beta, axis=1)
            else:
                break

        return beta, cost_history_fastgrad, beta_history

    def predict(self, X, beta):
        pred = 1 / (1 + np.exp(-X.T.dot(beta))) > 0.5
        predictions = pred * 2 - 1
        return predictions

    def mis_classification_error(self, X, y, beta):
        predictions = self.predict(X, beta)
        error = np.mean(predictions != y) * 100
        return error