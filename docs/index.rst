==================================
Assumption Free K-Means++ Seedings
==================================

.. toctree::
   :maxdepth: 2

   reference
   demo

Introduction
------------

This package contains sklearn compatible python implementations of various K-Means seeding algorithms.

The package was inspired by the AFKMC^2 algorithm detailed in

    |   **Fast and Provably Good Seedings for k-Means** [afkmc2]_
    |   Olivier Bachem, Mario Lucic, S. Hamed Hassani and Andreas Krause
    |   In *Neural Information Processing Systems* (NIPS), 2016.
    |   https://las.inf.ethz.ch/files/bachem16fast.pdf

The algorithm uses Monte Carlo Markov Chain to quickly find good seedings for KMeans and offers a runtime improvement over the common K-Means++ algorithm.

Usage
^^^^^

Using this package to get seedings for KMeans in sklearn is as simple as::

    import afkmc2
    X = np.array([[1, 2], [1, 4], [1, 0],
                 [4, 2], [4, 4], [4, 0]])
    seeds = afkmc2.afkmc2(X, 2)

    from sklearn.custer import KMeans
    model = KMeans(n_clusters=2, init=seeds).fit(X)
    print model.cluster_centers_

Installation
^^^^^^^^^^^^

Quickly install afkmc2 by running::

    pip install afkmc2

Contribute
^^^^^^^^^^

* Issue Tracker: https://github.com/adriangoe/afkmc2/issues
* Source Code: https://github.com/adriangoe/afkmc2

Support
^^^^^^^

You can reach out to me through https://adriangoe.me.


License
^^^^^^^

The project is licensed under the MIT License.
