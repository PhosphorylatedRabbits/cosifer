"""SNF combiner."""
import logging
from functools import reduce
import numpy as np
from rpy2.robjects.packages import importr
import rpy2.robjects.numpy2ri
from ..collections.graph import Graph
from .network_combiner import NetworkCombiner

logger = logging.getLogger(__name__.split('.')[-1])


def compute_snf(results_list, labels, K=20, T=10, snf=importr('SNFtool')):
    """
    Compute combination via SNF.

    Args:
        results_list (list): a list of InteractionTable objects.
        labels (list): labels to consider.
        K (int, optional): number of nearest neighbors. Defaults to 20.
        T (int, optional): number of steps in the diffusion process. Defaults
            to 10.
        snf (object, optional): SNF rpy2 object. Defaults to
            importr('SNFtool').

    Returns:
        Graph: the combined graph.
    """
    return Graph(
        np.array(
            snf.SNF(
                [
                    result_df.to_graph(imposed_labels=labels
                                       ).adjacency.todense()
                    for result_df in results_list
                ], K, T
            )
        )
    )


class SNF(NetworkCombiner):
    """
    Combine interaction tables representing networks using SNF.

    Attributes:
        interaction_symbol (str): symbol used to indicate
            interactions in the index of the dataframe.
        name (str): name of the combiner.
    """
    def __init__(self, interaction_symbol='<->', name='snf', **kwargs):
        """
        Intialize SNF combiner.

        Args:
            interaction_symbol (str, optional): symbol used to indicate
                interactions in the index of the dataframe.
                Defaults to '<->'.
            name (str, optional): name of the combiner. Defaults to 'snf'.
        """
        self.name = name
        super(SNF, self).__init__(**kwargs)
        self.interaction_symbol = interaction_symbol

    def _combine(self, results_list):
        """
        Apply the combination method via SNF and assign it to the graph.

        Args:
            results_list (list): a list of InteractionTable objects.
        """
        logger.debug('start combining')
        labels = sorted(
            list(
                reduce(
                    lambda a_set, another_set: a_set | another_set,
                    [set(result_df.labels) for result_df in results_list]
                )
            ),
            reverse=True
        )
        rpy2.robjects.numpy2ri.activate()
        snf = importr('SNFtool')
        self.graph = compute_snf(
            results_list, labels, snf=snf, **self.parameters
        )
        self.graph.set_labels(labels)
        logger.debug('finished combining')
        logger.debug('graph computed')

    def __str__(self):
        """
        Get the name of the combiner.

        Returns:
            str: name of the combiner.
        """
        return self.name
