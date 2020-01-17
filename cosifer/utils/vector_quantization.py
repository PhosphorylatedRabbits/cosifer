"""Vector quantization utilities."""
import numpy as np
from sklearn.cluster import KMeans


def k_means_bic(X, clusters_centers, clusters_labels, sigma_eps=1.):
    """
    Compute BIC for K-means clustering.

    Args:
        X (np.ndarray): clustered data.
        clusters_centers (np.ndarray): cluster centers.
        clusters_labels (np.ndarray): cluster labels.
        sigma_eps (float, optional): standard deviation. Defaults to 1..

    Returns:
        float: BIC score.
    """
    n, m = X.shape
    k, _ = clusters_centers.shape
    points = range(n)
    likelihood = (
        (
            (X[points, :] - clusters_centers[clusters_labels[points], :]) /
            sigma_eps
        )**2
    ).sum()
    return likelihood + m * k * np.log(n)


def k_means_optimized_with_bic(
    X, k_min=3, k_max=9, k_step=1, sigma_eps=1., n_init=100, **kwargs
):
    """
    Find an optimal K-mean model minizing the BIC score.

    Args:
        X (np.ndarray): data to cluster.
        k_min (int, optional): minimum number of clusters. Defaults to 3.
        k_max (int, optional): maximum number of clusters. Defaults to 9.
        k_step (int, optional): number of cluster steps. Defaults to 1.
        sigma_eps (float, optional): standard deviation. Defaults to 1..
        n_init (int, optional): number of K-means initializations.
            Defaults to 100.

    Returns:
        tuple: a tuple containing two elements: the first is the optimal model,
            the second one is a dictionary mapping the number of clusters to
            the BIC score.
    """
    if k_min >= k_max:
        k_max = k_min + k_step

    bic_dict = {}
    model_dict = {}

    for k in range(k_min, k_max + 1, k_step):
        model_dict[k] = KMeans(init='k-means++', n_clusters=k, **kwargs)
        model_dict[k].fit(X)
        bic_dict[k] = k_means_bic(
            X,
            model_dict[k].cluster_centers_,
            model_dict[k].labels_,
            sigma_eps=sigma_eps
        )
    min_key = min(bic_dict, key=bic_dict.get)
    return model_dict[min_key], bic_dict


def k_means_vector_quantization(
    x, k_min=3, k_max=9, k_step=1, sigma_eps=1., n_init=100, **kwargs
):
    """
    Quantize a vector using K-means optimized via BIC score.

    Args:
        x (np.ndarray): array to quantize.
        k_min (int, optional): minimum number of clusters. Defaults to 3.
        k_max (int, optional): maximum number of clusters. Defaults to 9.
        k_step (int, optional): number of cluster steps. Defaults to 1.
        sigma_eps (float, optional): standard deviation. Defaults to 1..
        n_init (int, optional): number of K-means initializations.
            Defaults to 100.

    Returns:
        np.ndarray: the quantized vector.
    """
    assert x.shape[1] == 1
    if k_min >= k_max:
        k_max = k_min + k_step

    model, _ = k_means_optimized_with_bic(
        x,
        k_min=k_min,
        k_max=k_max,
        k_step=k_step,
        sigma_eps=sigma_eps,
        **kwargs
    )

    sorted_centers_indices = np.argsort(np.ravel(model.cluster_centers_))
    remapping = np.zeros(len(sorted_centers_indices), dtype=int)
    for idx, cluster_idx in enumerate(sorted_centers_indices):
        remapping[cluster_idx] = idx

    return remapping[model.labels_]
