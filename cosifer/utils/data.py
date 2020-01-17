"""Data utilities."""
import logging
import re
import numpy as np
import pandas as pd
from numpy.linalg import linalg
from sklearn.datasets import make_sparse_spd_matrix

logger = logging.getLogger(__name__.split('.')[-1])

MORE_THAN_ONE_WHITESPACE_REGEX = re.compile(r'\s+')


def read_data(
    filepath,
    standardize=True,
    samples_on_rows=True,
    sep='\t',
    fillna=0.,
    **kwargs
):
    """
    Read data from file.

    Args:
        filepath (str): path to the file.
        standardize (bool, optional): toggle data standardization.
            Defaults to True.
        samples_on_rows (bool, optional): flag to indicate whether data are
            following the format where each row represents a sample.
            Defaults to True.
        sep (str, optional): field separator. Defaults to '\t'.
        fillna (float, optional): value used to fill NAs. Defaults to 0.

    Returns:
        pd.DataFrame: a dataframe parsed from the provided filepath.
    """
    _ = kwargs.pop('sep', None)
    data = pd.read_table(filepath, sep=sep, **kwargs)
    if not samples_on_rows:
        data = data.T
    if standardize:
        data = (data - data.mean()) / data.std()
    data = data.dropna(how='all', axis=1)
    if fillna is not None:
        data = data.fillna(fillna)
    return data


def get_synthetic_data(
    n_samples, n_features, precision_matrix=None, alpha=0.98, seed=1
):
    """
    Generate synthetic data using a covariance matrix obtained by inverting
    a randomly generated precision matrix.

    Args:
        n_samples ([type]): [description]
        n_features ([type]): [description]
        precision_matrix ([type], optional): [description]. Defaults to None.
        alpha (float, optional): [description]. Defaults to 0.98.
        seed (int, optional): [description]. Defaults to 1.

    Returns:
        tuple: a tuple with two elements. The first is a pd.DataFrame
            represeting the data. The second is the precision matrix used to
            generate the data.
    """
    prng = np.random.RandomState(seed)
    if precision_matrix is None:
        prec = make_sparse_spd_matrix(
            n_features,
            alpha=alpha,
            smallest_coef=.1,
            largest_coef=.9,
            random_state=prng
        )
    else:
        prec = precision_matrix
    cov = linalg.inv(prec)
    d = np.sqrt(np.diag(cov))
    cov /= d
    cov /= d[:, np.newaxis]
    prec *= d
    prec *= d[:, np.newaxis]
    X = prng.multivariate_normal(np.zeros(n_features), cov, size=n_samples)
    X -= X.mean(axis=0)
    X /= X.std(axis=0)

    X = pd.DataFrame(X)

    X.columns = ["gene" + str(i) for i in X.columns]
    X.index = ["sample" + str(i) for i in X.index]

    return X, prec


def scale_graph(graph, threshold=.0):
    """
    Min-max scale a matrix representing a graph assuming poitive values.

    Args:
        graph (pd.DataFrame): a dataframe representing a graph.
        threshold (float, optional): threshold to impose on the edge weights.
            Defaults to .0.

    Returns:
        pd.DataFrame: a dataframe representing the scaled graph.
    """
    scaled_graph = np.abs(graph)
    max_value = max(scaled_graph.values.flatten())
    scaled_graph /= max_value
    np.fill_diagonal(scaled_graph.values, .0)
    scaled_graph[scaled_graph < threshold] = .0
    return scaled_graph


def read_gmt(filepath):
    """
    Read a GMT file.

    Args:
        filepath (str): path to a GMT file.

    Returns:
        dict: a dictionary containing sets of features.
    """
    sets = dict()
    with open(filepath, 'rb') as fp:
        for line in fp:
            splitted = MORE_THAN_ONE_WHITESPACE_REGEX.split(
                line.strip().decode()
            )
            sets[splitted[0]] = set(splitted[2:])
    return sets
