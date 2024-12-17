import numpy as np

class KMeansCustom:
    def __init__(self, n_clusters=3, max_iter=300, tol=1e-4, random_state=None):
        """
        Custom implementation of KMeans clustering.
        :param n_clusters: Number of clusters
        :param max_iter: Maximum number of iterations
        :param tol: Tolerance to declare convergence
        :param random_state: Seed for reproducibility
        """
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state

    def fit(self, X):
        """
        Fit the KMeans model to the data.
        :param X: Input data, a numpy array of shape (n_samples, n_features)
        """
        np.random.seed(self.random_state)

        # Randomly initialize centroids
        initial_indices = np.random.choice(X.shape[0], self.n_clusters, replace=False)
        self.centroids = X[initial_indices]

        for i in range(self.max_iter):
            # Assign clusters based on the closest centroid
            self.labels = self._assign_clusters(X)

            # Calculate new centroids as the mean of the assigned points
            new_centroids = np.array([X[self.labels == k].mean(axis=0) for k in range(self.n_clusters)])

            # Check for convergence
            if np.all(np.abs(new_centroids - self.centroids) < self.tol):
                break

            self.centroids = new_centroids

    def predict(self, X):
        """
        Predict the cluster for each sample in X.
        :param X: Input data, a numpy array of shape (n_samples, n_features)
        :return: Cluster labels for each sample
        """
        return self._assign_clusters(X)

    def _assign_clusters(self, X):
        """
        Assign clusters based on the closest centroid.
        :param X: Input data
        :return: Array of cluster labels
        """
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
        return np.argmin(distances, axis=1)
