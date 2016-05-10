import numpy as np

__author__ = "Ivan Sevcik"

class PCA(object):
    mean = None
    eigen_values = None
    eigen_vectors = None

    def __init__(self):
        pass

    @staticmethod
    def project(W, X, mu=None):
        if mu is None:
            return np.dot(X, W)
        return np.dot(X - mu, W)

    def project(self, X):
        return np.dot(X - self.mean, self.eigen_vectors)

    def get_allowed_deviation(self):
        return 3 * np.sqrt(self.eigen_values)

    @staticmethod
    def reconstruct(W, Y, mu=None):
        if mu is None:
            return np.dot(Y, W.T)
        return np.dot(Y, W.T) + mu

    def reconstruct(self, Y):
        return np.dot(Y, self.eigen_vectors.T) + self.mean

    def train(self, X, num_components=0):
        [n, d] = X.shape
        if (num_components <= 0) or (num_components > n):
            num_components = n
        mu = X.mean(axis=0)
        X = X - mu
        if n > d:
            C = np.dot(X.T, X) / (X.shape[0] - 1)
            [eigenvalues, eigenvectors] = np.linalg.eigh(C)
        else:
            C = np.dot(X, X.T) / (X.shape[1] - 1)
            [eigenvalues, eigenvectors] = np.linalg.eigh(C)
            eigenvectors = np.dot(X.T, eigenvectors)
            for i in xrange(n):
                eigenvectors[:, i] = eigenvectors[:, i] / np.linalg.norm(eigenvectors[:, i])
        # or simply perform an economy size decomposition
        # eigenvectors, eigenvalues, variance = np.linalg.svd(X.T, full_matrices=False)
        # sort eigenvectors descending by their eigenvalue
        idx = np.argsort(-eigenvalues)
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        # select only num_components
        eigenvalues = eigenvalues[0:num_components].copy()
        eigenvectors = eigenvectors[:, 0:num_components].copy()

        result = [eigenvalues, eigenvectors, mu]
        self.eigen_values, self.eigen_vectors, self.mean = result
        return result

    def threshold(self, value):
        # Limit the value into acceptable region
        value = max(0., min(value, 1.))

        # Compute explained variance
        # Source: https://plot.ly/ipython-notebooks/principal-component-analysis/
        tot = sum(self.eigen_values)
        var_exp = self.eigen_values / tot
        cum_var_exp = np.cumsum(var_exp)

        # Find required threshold
        i = 0
        while i < len(self.eigen_values) - 1 and cum_var_exp[i] < value:
            i += 1

        # Limit arrays
        self.eigen_values = self.eigen_values[:i+1]
        self.eigen_vectors = self.eigen_vectors[:, :i+1]

        pass
