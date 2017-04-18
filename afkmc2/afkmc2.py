"""Python Implementation of Fast and Provably Good Seedings for k-Means

> Fast and Provably Good Seedings for k-Means
> Olivier Bachem, Mario Lucic, S. Hamed Hassani and Andreas Krause
> In Neural Information Processing Systems (NIPS), 2016.

Usage:
>>> import afkmc2
>>> X = np.array with d-dimensional data
>>> seeds = afkmc2.afkmc2(X, 3)

Use seeds in sklearn KMeans:
>>> from sklearn.custer import KMeans
>>> model = KMeans(3, init=seeds).fit(X)
>>> print model.cluster_centers_
"""
import numpy as np


def kmpp(X, k):
    """KMeans++ Seeding as described by Arthur and Vassilvitskii (2007)
    runs in O(nkd)

    Args:
        X: np.array with datapoints. shape: n, d
        k: Number cluster centers
        m: length of markov chain. Default: 200

    Returns:
        np.array with cluster centers for seeding. shape: k, d
    """
    centers = np.zeros((k, X.shape[1]), dtype=np.float)

    # Sample first center uniformly
    centers[0, :] = X[np.random.choice(X.shape[0]), :]

    for i in range(1, k):
        # Get distance to closest center for each point
        D2 = np.array([min([np.linalg.norm(x-centers[j, :])**2
                       for j in range(i)]) for x in X])

        # Choose new center with high prob if far from all other centers
        probs = D2/np.sum(D2)
        cumprobs = probs.cumsum()
        r = np.random.uniform()
        ind = np.where(cumprobs >= r)[0][0]

        # Store chosen center
        centers[i] = X[ind, :]

    return centers


def kmc2(X, k, m=200):
    """KMC^2 Seeding in O(nd + mk^2d) as described by
    Bachem, Lucic, Hassani and Krause (2016)

    Args:
        X: np.array with datapoints. shape: n, d
        k: Number cluster centers
        m: length of markov chain. Default: 200

    Returns:
        np.array with cluster centers for seeding. shape: k, d
    """
    centers = np.zeros((k, X.shape[1]), dtype=np.float)

    # Sample first center uniformly
    centers[0, :] = X[np.random.choice(X.shape[0]), :]

    # k-1 iterations
    for i in range(1, k):
        # Sample initial point of Markov Chain
        x = np.random.choice(X.shape[0])
        # Get shortest distance from previous centers
        dx2 = min([np.linalg.norm(X[x, :]-centers[j, :])**2 for j in range(i)])

        # m-1 more candidates
        for j in range(1, m):
            # New Sample
            y = np.random.choice(X.shape[0])
            dy2 = min([np.linalg.norm(X[y, :]-centers[j, :])**2
                      for j in range(i)])
            # Move to candidate according to acceptance prob based on distances
            if dy2/dx2 > np.random.uniform():
                x = y
                dx2 = dy2

        # Store current choice after m samples
        centers[i] = X[x, :]

    return centers


def afkmc2(X, k, m=200):
    """Python Assumption Free KMC^2 Seeding in O(nd + mk^2d)

    Args:
        X: np.array with datapoints. shape: n, d
        k: Number cluster centers
        m: length of markov chain. Default: 200
        af: Use assumption free algorithm (true) or uniform assumption (false)
        memo: Memoize distances

    Returns:
        np.array with cluster centers for seeding. shape: k, d
    """
    centers = np.zeros((k, X.shape[1]), dtype=np.float)

    # Sample first center uniformly
    centers[0, :] = X[np.random.choice(X.shape[0]), :]

    # Create assumption free proposal distribution: O(n)
    d2 = [np.linalg.norm(X[i, :]-centers[0, :])**2
          for i in range(X.shape[0])]
    q = d2/(2*np.sum(d2)) + 1/(2.0*X.shape[0])

    # k-1 iterations
    for i in range(1, k):
        # Sample initial point of Markov Chain
        x = np.random.choice(X.shape[0], p=q)
        # Get shortest distance from previous centers
        dx2 = min([np.linalg.norm(X[x, :]-centers[j, :])**2 for j in range(i)])

        # m-1 more candidates
        for j in range(1, m):
            # New Sample
            y = np.random.choice(X.shape[0], p=q)
            dy2 = min([np.linalg.norm(X[y, :]-centers[j, :])**2
                      for j in range(i)])
            # Move to candidate according to acceptance prob based on distances
            if (dy2*q[x])/(dx2*q[y]) > np.random.uniform():
                x = y
                dx2 = dy2

        # Store current choice after m samples
        centers[i] = X[x, :]

    return centers


def afkmc2_mem(X, k, m=200):
    """Python Assumption Free KMC^2 Seeding in O(nd + mk^2d)
    Uses O(kn) additional space to store distances. Upper bound
    remains the same, but for small datasets speedup is significant
    (when n is not much bigger than m)

    Args:
        X: np.array with datapoints. shape: n, d
        k: Number cluster centers
        m: length of markov chain. Default: 200

    Returns:
        np.array with cluster centers for seeding. shape: k, d
    """
    centers = np.zeros((k, X.shape[1]), dtype=np.float)

    # Sample first center uniformly
    centers[0, :] = X[np.random.choice(X.shape[0]), :]

    # Distance memoization
    d_store = np.empty((X.shape[0], k))

    def distance(i, j):
        """Get squared distance between node and one of the centers

        Args:
            i: Index in data array
            j: Index of cluster center
        Returns:
            Squared Distance between X[i, :] and centers[j, :]
        """
        if not d_store[i, j]:
            d_store[i, j] = np.linalg.norm(X[i, :]-centers[j, :])**2
        return d_store[i, j]

    # Create assumption free proposal distribution: O(n)
    d2 = [distance(i, 0)
          for i in range(X.shape[0])]
    q = d2/(2*np.sum(d2)) + 1/(2.0*X.shape[0])

    # k-1 iterations
    for i in range(1, k):
        # Sample initial point of Markov Chain
        x = np.random.choice(X.shape[0], p=q)
        # Get shortest distance from previous centers
        dx2 = min([distance(x, j) for j in range(i)])

        # m-1 more candidates
        for j in range(1, m):
            # New Sample
            y = np.random.choice(X.shape[0], p=q)
            dy2 = min([distance(y, j)
                      for j in range(i)])
            # Move to candidate according to acceptance prob based on distances
            if (dy2*q[x])/(dx2*q[y]) > np.random.uniform():
                x = y
                dx2 = dy2

        # Store current choice after m samples
        centers[i] = X[x, :]

    return centers
