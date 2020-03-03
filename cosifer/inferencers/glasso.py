"""Glasso inferencer."""
import logging
import pandas as pd
from sklearn.covariance import GraphicalLassoCV
from ..collections.graph import Graph
from .network_inferencer import NetworkInferencer
from ..utils.stats import from_precision_matrix_partial_correlations

logger = logging.getLogger(__name__.split('.')[-1])


class Glasso(NetworkInferencer):
    """
    Glasso inferencer.

    Attributes:
        method (str): name of the method.
    """

    def __init__(self, correction=None, method='gLasso', **kwargs):
        """
        Initialize the Glasso inferencer.

        Args:
            method (str, optional): name of the method. Defaults to 'gLasso'.
        """
        self.method = method
        super().__init__(**kwargs)

    def _infer_network(self, data):
        """
        Infer the network.

        Args:
            data (pd.DataFrame): data to be used for the inference.
        """
        entities = data.columns
        model = GraphicalLassoCV(**self.parameters)
        model.fit(data.values)
        self.graph = Graph(
            adjacency=pd.DataFrame(
                from_precision_matrix_partial_correlations(model.precision_),
                index=entities,
                columns=entities
            )
        )
        logger.debug('inferred with {}'.format(self.method))

    def __str__(self):
        """
        Get the name of the inferencer.

        Returns:
            str: name of the inferencer: glasso.
        """
        return 'glasso'
