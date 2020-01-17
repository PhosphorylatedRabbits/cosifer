"""FunChisq inferencer."""
import logging
import pandas as pd
import numpy as np
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
from ..collections.interaction_table import InteractionTable
from .network_inferencer import NetworkInferencer
from ..utils.stats import CORRECTIONS
from ..utils.vector_quantization import k_means_vector_quantization

logger = logging.getLogger(__name__.split('.')[-1])


class FunChisq(NetworkInferencer):
    """
    FunChisq inferencer.

    Attributes:
        k_min (int): minimum number of quantization bins.
        k_max (int): maximum number of quantization bins.
        k_step (int): number of steps for bins search.
        method (str): name of the method.
        correction (str): correction method.
        confidence_threshold (float): confidence threshold.
        undirected (bool): flag to indicate an undirected network.
    """

    def __init__(
        self,
        k_min=3,
        k_max=7,
        k_step=1,
        method='FunChisq',
        correction=None,
        confidence_threshold=.05,
        undirected=True,
        **kwargs
    ):
        """
        Initialize FunChisq inferencer.

        Args:
            k_min (int, optional): minimum number of quantization bins.
                Defaults to 3.
            k_max (int, optional): maximum number of quantization bins.
                Defaults to 7.
            k_step (int, optional): number of steps for bins search.
                Defaults to 1.
            method (str, optional): name of the method. Defaults to 'FunChisq'.
            correction ([type], optional): correction method. Defaults to None.
            confidence_threshold (float, optional): confidence threshold.
                Defaults to .05.
            undirected (bool, optional): flag to indicate an undirected
                network. Defaults to True.
        """
        self.k_min = k_min
        self.k_max = k_max
        self.k_step = k_step
        self.method = method
        self.correction = correction
        self.confidence_threshold = confidence_threshold
        self.undirected = undirected
        super().__init__(**kwargs)

    def _infer_network(self, data):
        """
        Infer the network.

        Args:
            data (pd.DataFrame): data to be used for the inference.
        """
        # quantization step with optimal k based on BIC
        quantized = data.apply(
            lambda column: k_means_vector_quantization(
                column.values.reshape(-1, 1),
                k_min=self.k_min,
                k_max=self.k_max,
                k_step=self.k_step,
                **self.parameters
            ),
            axis=0
        )
        entities = data.columns
        number_of_entities = len(entities)
        # activate implicit conversion from pandas to R objects
        pandas2ri.activate()
        fun_chisq = importr('FunChisq')
        # preparing variables to pass to FunChisq
        independent_variables = None
        dependent_variables = np.array([], dtype=int)
        ne_range = range(1, number_of_entities + 1)
        for index, entity in enumerate(entities):
            r_index = index + 1
            dependent_variables = np.hstack(
                [
                    dependent_variables,
                    np.array(
                        list(
                            filter(
                                lambda e_index: e_index != r_index, ne_range
                            )
                        )
                    )
                ]
            )
            if independent_variables is None:
                independent_variables = np.vstack(
                    [np.array(r_index) for _ in range(number_of_entities - 1)]
                )
            else:
                independent_variables = np.vstack(
                    [
                        independent_variables,
                        np.vstack(
                            [
                                np.array(r_index)
                                for _ in range(number_of_entities - 1)
                            ]
                        )
                    ]
                )
        # running FunChisq
        interactions = pandas2ri.ri2py(
            fun_chisq.test_interactions(
                quantized.T.values, list(independent_variables),
                pd.Series(dependent_variables), entities.values
            )
        )
        # test correction
        if self.correction in CORRECTIONS:
            significants = CORRECTIONS[self.correction](
                interactions['p.value'], self.confidence_threshold
            )
            interactions = interactions.iloc[significants]
        interactions.columns = [
            'gene1', 'gene2', 'p-value', 'statistic', 'estimate'
        ]
        # if undirected keep only interaction with higher importance if
        # both directions are significant
        if self.undirected is True:
            interactions = interactions.apply(
                lambda row: pd.Series(sort_interaction_entities(row)), axis=1
            )
            interactions.columns = [
                'gene1', 'gene2', 'p-value', 'statistic', 'estimate'
            ]
            interactions['grouping'] = [
                '{}_{}'.format(*sorted(pair))
                for pair in zip(interactions['gene1'], interactions['gene2'])
            ]
            selected_interactions = interactions.groupby(
                ['grouping']
            )['p-value'].transform(min) == interactions['p-value']
            interactions = interactions[selected_interactions]
        # prepare the interactions
        interactions = interactions[['gene1', 'gene2', 'statistic']]
        interactions.columns = ['e1', 'e2', 'intensity']
        self.graph = InteractionTable(df=interactions
                                      ).to_graph(undirected=self.undirected)
        logger.debug('inferred with {}'.format(self.method))

    def __str__(self):
        """
        Get the name of the inferencer.

        Returns:
            str: name of the inferencer: funchisq.
        """
        return 'funchisq'


def sort_interaction_entities(row):
    """
    Sort the entities over a row in lexicographic order.

    Args:
        row (pd.Series): row containing the entities to be sorted.

    Returns:
        list: a list containing the sorted entities and the rest of the
            elements of the row unchanged.
    """
    sorted_entities = sorted([row['gene1'], row['gene2']])
    return sorted_entities + list(row[2:])
