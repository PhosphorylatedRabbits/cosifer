"""Correlation inferencer."""
import logging
import numpy as np
import sys
import scipy.sparse as ss
from scipy.special import betainc
from ..collections.graph import Graph
from .network_inferencer import NetworkInferencer
from ..utils.stats import CORRECTIONS_SIGNIFICANCE

logger = logging.getLogger(__name__.split('.')[-1])

correlation_preprocess = {
    'pearson': lambda x: x.values.T,
    'spearman': lambda x: x.rank().values.T
}


class Correlation(NetworkInferencer):
    """
    Correlation inferencer.

    Attributes:
        method (str): correlation method.
        correction (str): correction method.
        confidence_threshold (float): confidence threshold.
    """

    method = None

    def __init__(
        self,
        method=method,
        correction=None,
        confidence_threshold=0.05,
        **kwargs
    ):
        """
        Initialize correlation inferencer.

        Args:
            method (str, optional): correlation method. Defaults to method.
            correction (str, optional): correction method. Defaults to None.
            confidence_threshold (float, optional): confidence threshold.
                Defaults to 0.05.
        """
        self.method = method
        self.correction = correction
        self.confidence_threshold = confidence_threshold
        super().__init__(**kwargs)

    def _infer_network(self, data):
        """
        Infer the network.

        Args:
            data (pd.DataFrame): data to be used for the inference.
        """
        logger.debug('inferring with {} correlation'.format(self.method))
        entities = data.columns
        # compute correlations
        pre_processed = correlation_preprocess[self.method](data)
        rho = np.corrcoef(pre_processed)
        n = rho.shape[0]
        logger.debug('computed correlation')
        # compute corrections mask
        if self.correction in CORRECTIONS_SIGNIFICANCE:
            triu_indices = np.triu_indices(n, 1)
            rhof = rho[triu_indices]
            dof = pre_processed.shape[1] - 2
            ts = rhof * rhof * (
                dof / (1 - rhof * rhof + sys.float_info.epsilon)
            )
            pf = betainc(0.5 * dof, 0.5, dof / (dof + ts))
            significants = CORRECTIONS_SIGNIFICANCE[
                self.correction](pf, self.confidence_threshold)
            mask = ss.lil_matrix(rho.shape, dtype=np.int8)
            mask[triu_indices] = significants
            mask += (mask.T + ss.eye(n, dtype=np.uint8))
            rho = mask.multiply(rho)
        self.graph = Graph(adjacency=rho, labels=entities.values)
        logger.debug('inferred with {} correlation'.format(self.method))

    def __str__(self):
        """
        Get the name of the inferencer.

        Returns:
            str: name of the inferencer.
        """
        return self.method
