"""JRF inferencer."""
import logging
import numpy as np
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
from ..collections.interaction_table import InteractionTable
from .network_inferencer import NetworkInferencer

logger = logging.getLogger(__name__.split('.')[-1])


class JointRandomForest(NetworkInferencer):
    """
    JRF inferencer.

    Attributes:
        ntree (int): number of trees.
        mtry (int): number of variables for splitting.
        merger (function): a merger function.
        method (str): name of the method.
    """

    def __init__(
        self,
        ntree=500,
        mtry=None,
        merger=lambda x, y: x + y,
        correction=None,
        method='JRF',
        **kwargs
    ):
        """
        Initialize the JRF inferencer.

        Args:
            ntree (int, optional): number of trees. Defaults to 500.
            mtry (int, optional): number of variables for splitting.
                Defaults to None.
            merger (function, optional): a merger function. Defaults to sum.
            method (str, optional): name of the method. Defaults to 'JRF'.
        """
        self.ntree = ntree
        self.mtry = mtry
        self.merger = merger
        self.method = method
        super().__init__(**kwargs)

    def _infer_network(self, data):
        """
        Infer the network.

        Args:
            data (pd.DataFrame): data to be used for the inference.
        """
        if isinstance(data, list):
            self._infer_from_data_list(data)
        else:
            self._infer_from_single_data(data)

    def _infer_from_single_data(self, data):
        """
        Infer the network from a single dataframe.

        Args:
            data (pd.DataFrame): data to be used for the inference.
        """
        entities = data.columns
        number_of_predictors = len(entities) - 1
        # activate implicit conversion from pandas to R objects
        pandas2ri.activate()
        jrf = importr('JRF')
        if self.mtry and self.mtry > number_of_predictors:
            logger.error(
                "mtry={} > candidate predictors={}.".format(
                    self.mtry, number_of_predictors
                )
            )
            raise RuntimeError('mtry is bigger than the number of predictors.')
        interactions = pandas2ri.ri2py(
            jrf.JRF(
                [data.T.values], self.ntree,
                self.mtry if self.mtry else int(np.sqrt(number_of_predictors)),
                entities
            )
        )
        interactions.columns = ['e1', 'e2', 'intensity']
        self.graph = InteractionTable(df=interactions).to_graph()
        logger.debug('inferred with {}'.format(self.method))

    def _infer_from_data_list(self, data_list):
        """
        Infer the network from a list of dataframes.

        Args:
            data (list): list of data to be used for the inference.
        """
        entities = data_list[0].columns
        number_of_predictors = len(entities) - 1
        # activate implicit conversion from pandas to R objects
        pandas2ri.activate()
        jrf = importr('JRF')
        if self.mtry and self.mtry > number_of_predictors:
            logger.error(
                "mtry={} > candidate predictors={}.".format(
                    self.mtry, number_of_predictors
                )
            )
            raise RuntimeError('mtry is bigger than the number of predictors.')
        interactions = pandas2ri.ri2py(
            jrf.JRF(
                [data.T.values for data in data_list], self.ntree,
                self.mtry if self.mtry else int(np.sqrt(number_of_predictors)),
                entities
            )
        )
        importance_columns = (
            interactions.columns[
                interactions.columns.str.startswith('importance')]
        )
        logger.debug(importance_columns)
        interactions['merged_importance'] = interactions[importance_columns
                                                         ].mean(axis=1)
        interactions = interactions.drop(importance_columns, axis=1)
        interactions.columns = ['e1', 'e2', 'intensity']
        self.graph = InteractionTable(df=interactions).to_graph()
        logger.debug('inferred with {}'.format(self.method))

    def __str__(self):
        """
        Get the name of the inferencer.

        Returns:
            str: name of the inferencer: jrf.
        """
        return 'jrf'
