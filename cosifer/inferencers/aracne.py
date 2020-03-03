"""Aracne inferencer."""
import logging
import pandas as pd
import numpy as np
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri, globalenv, r
from rpy2.robjects.packages import importr
from ..collections.graph import Graph
from .network_inferencer import NetworkInferencer

logger = logging.getLogger(__name__.split('.')[-1])


class Aracne(NetworkInferencer):
    """
    Aracne inferencer implementation.

    Attributes:
        estimator (str): estimator type.
        disc (str): discretization type.
        method (str): name of the method.
    """

    def __init__(self, estimator, disc='none', method='ARACNE', **kwargs):
        """
        Initialize Aracne inferencer.

        Args:
            estimator (str): estimator type. Choose one from 'spearman',
                'pearson' and 'kendall'.
            disc (str, optional): discretization type. Defaults to 'none'.
            method (str, optional): name of the method. Defaults to 'ARACNE'.
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
        globalenv['n_bins'] = np.sqrt(len(data.index))
        globalenv['estimator'] = self.estimator
        globalenv['disc'] = self.disc
        # compute mutual information matrix
        globalenv['data'] = ro.conversion.py2rpy(data)
        r('''
        mim <- build.mim(
            data, estimator=estimator,
            disc=disc, nbins=n_bins
        )
        ''')
        mim = globalenv['mim']
        # run Aracne
        weight_matrix = ro.conversion.rpy2py(minet.aracne(mim, eps=0.2))
        weight_matrix = pd.DataFrame(
            weight_matrix, columns=data.columns, index=data.columns
        )
        self.graph = Graph(adjacency=weight_matrix)
        logger.debug('inferred with {}'.format(self.method))

    def __str__(self):
        """
        Get the name of the inferencer.

        Returns:
            str: name of the inferencer: aracne.
        """
        return 'aracne'
