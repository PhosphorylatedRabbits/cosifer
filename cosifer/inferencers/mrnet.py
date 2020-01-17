"""MRNET inferencer."""
import logging
import pandas as pd
import numpy as np
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
from ..collections.graph import Graph
from .network_inferencer import NetworkInferencer

logger = logging.getLogger(__name__.split('.')[-1])


class MRNET(NetworkInferencer):
    """
    MRNET inferencer.

    Attributes:
        estimator (str): estimator type.
        disc (str): discretization type.
        method (str): name of the method.
    """

    def __init__(self, estimator, disc='none', method='MRNET', **kwargs):
        """
        Initialize MRNET inferencer.

        Args:
            estimator (str): estimator type. Choose one from 'spearman',
                'pearson' and 'kendall'.
            disc (str, optional): discretization type. Defaults to 'none'.
            method (str, optional): name of the method. Defaults to 'MRNET'.
        """
        self.estimator = estimator
        self.disc = disc
        self.method = method

        super().__init__(**kwargs)

    def _infer_network(self, data):
        """
        Infer the network.

        Args:
            data (pd.DataFrame): data to be used for the inference.
        """
        # activate implicit conversion from pandas to R objects
        pandas2ri.activate()
        minet = importr('minet')
        # compute number of bins
        self.n_bins = np.sqrt(len(data.index))
        # run MRNET
        weight_matrix = pandas2ri.ri2py(
            minet.minet(
                pandas2ri.py2ri(data),
                method='mrnet',
                estimator=self.estimator,
                disc=self.disc,
                nbins=self.n_bins
            )
        )
        weight_matrix = pd.DataFrame(
            weight_matrix, columns=data.columns, index=data.columns
        )
        self.graph = Graph(adjacency=weight_matrix)
        logger.debug('inferred with {}'.format(self.method))

    def __str__(self):
        """
        Get the name of the inferencer.

        Returns:
            str: name of the inferencer: mrnet.
        """
        return 'mrnet'
