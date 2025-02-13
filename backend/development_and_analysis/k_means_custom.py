import numpy as np

class CustomKMeans:
    def __init__(self, n_clusters=2, max_iters=100, tol=1e-4, random_state=42):
        self.n_clusters = n_clusters
        self.max_iters = max_iters
        self.tol = tol  # Convergence threshold
        self.random_state = random_state
        self.centroids = None

    def initialize_centroids(self, X):
        """Initialize centroids using K-Means++ initialization."""
        np.random.seed(self.random_state)
        centroids = [X[np.random.choice(X.shape[0])]]
        
        for _ in range(1, self.n_clusters):
            distances = np.min([np.linalg.norm(X - c, axis=1) for c in centroids], axis=0)
            probabilities = distances / distances.sum()
            new_centroid = X[np.random.choice(X.shape[0], p=probabilities)]
            centroids.append(new_centroid)
        
        return np.array(centroids)

    def fit(self, X):
        """Run K-Means clustering on the dataset X."""
        self.centroids = self.initialize_centroids(X)

        for _ in range(self.max_iters):
            # Step 2: Assign each point to the closest centroid
            distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)  # Compute distances
            labels = np.argmin(distances, axis=1)  # Assign clusters

            # Step 3: Compute new centroids
            new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(self.n_clusters)])

            # Step 4: Check for convergence
            if np.linalg.norm(self.centroids - new_centroids) < self.tol:
                break  # Stop if centroids do not change significantly

            self.centroids = new_centroids  # Update centroids

        return labels

    def predict(self, X):
        """Assign clusters based on the fitted centroids."""
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
        return np.argmin(distances, axis=1)
