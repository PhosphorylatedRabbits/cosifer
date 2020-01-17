"""Statistics utils."""
import numpy as np
import pandas as pd
from statsmodels.stats import multitest as mt
from .data import scale_graph


def bonferroni_correction(p_values, q_star):
    """
    Return indices of pValues that make reject null hypothesis
    at given significance level with a Bonferroni correction.
    Used implementation robust to nan values through statsmodels.

    Args:
        p_values (iterable): p-values to be used for correction.
        q_star (float): false discovery rate.

    Returns:
        list: indices of significant p-values.
    """
    return [
        idx for idx, significant in
        enumerate(mt.multipletests(p_values, alpha=q_star, method='b')[0])
        if significant
    ]


def benjamini_hochberg_correction(p_values, q_star):
    """
    Return indices of pValues that make reject null hypothesis
    at given significance level with a Benjamini-Hochberg correction.
    Used implementation robust to nan values through statsmodels.

    Args:
        p_values (iterable): p-values to be used for correction.
        q_star (float): false discovery rate.

    Returns:
        list: indices of significant p-values.
    """
    return [
        idx for idx, significant in enumerate(
            mt.multipletests(p_values, alpha=q_star, method='fdr_bh')[0]
        ) if significant
    ]


def benjamini_yekutieli_correction(p_values, q_star):
    """
    Return indices of pValues that make reject null hypothesis
    at given significance level with a Benjamini-Yekutieli correction.
    Used implementation robust to nan values through statsmodels.

    Args:
        p_values (iterable): p-values to be used for correction.
        q_star (float): false discovery rate.

    Returns:
        list: indices of significant p-values.
    """
    return [
        idx for idx, significant in enumerate(
            mt.multipletests(p_values, alpha=q_star, method='fdr_by')[0]
        ) if significant
    ]


CORRECTIONS = {
    'bonferroni': lambda p, t: bonferroni_correction(p, t),
    'b-h': lambda p, t: benjamini_hochberg_correction(p, t),
    'b-y': lambda p, t: benjamini_yekutieli_correction(p, t)
}

CORRECTIONS_SIGNIFICANCE = {
    'bonferroni': lambda p, t: mt.multipletests(p, alpha=t, method='b')[0],
    'b-h': lambda p, t: mt.multipletests(p, alpha=t, method='fdr_bh')[0],
    'b-y': lambda p, t: mt.multipletests(p, alpha=t, method='fdr_by')[0]
}


def from_precision_matrix_partial_correlations(precision, scaled=False):
    """
    Compute partial correlations from the precision matrix.

    Args:
        precision (np.ndarray): a precision matrix.
        scaled (bool, optional): flag to min-max scale the correlations.
            Defaults to False.

    Returns:
        np.ndarray: the partial correlation matrix.
    """
    diag = np.diag(precision)
    cross_diagonal_sqrt = np.sqrt(np.outer(diag, diag))
    partial_correlations = -precision / cross_diagonal_sqrt
    np.fill_diagonal(partial_correlations, 1.)
    return (
        scale_graph(pd.DataFrame(partial_correlations)).values
        if scaled else partial_correlations
    )
