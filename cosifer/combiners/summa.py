"""Combiner using SUMMA."""
import logging
import numpy as np
import pandas as pd
from pySUMMA import Summa as _summa
from .network_combiner import NetworkCombiner
from .core import concatenate_intensities, combined_df_to_interaction_table

logger = logging.getLogger(__name__.split('.')[-1])


def fill_na_ranks(a_series):
    """
    Fill NA ranks in a pd.Series.

    Args:
        a_series (pd.Series): series to fill.

    Returns:
        pd.Series: the filled series.
    """
    a_filled_series = a_series.copy()
    is_na = pd.isna(a_filled_series)
    if is_na.sum() > 0:
        fill_values = np.arange(1, is_na.sum() + 1)
        a_filled_series += fill_values[-1]
        a_filled_series[is_na] = fill_values
    return a_filled_series


def summa_scores_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Apply SUMMA as a method on list of interaction tables.

    Args:
        table_list (list): a list of InteractionTable objects.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe.
            Defaults to '<->'.
    Returns:
        InteractionTable: interaction table with SUMMA scores.
    """
    if len(table_list) == 1:
        return table_list[0]
    df = concatenate_intensities(table_list, **kwargs)
    data = df.rank(ascending=False,
                   method='first').apply(fill_na_ranks,
                                         axis=0).values.T.astype(int)
    summa = _summa()
    summa.fit(data)
    scores = summa.get_scores(data)
    scores -= scores.min()
    scores /= scores.max()
    combined = pd.Series(scores, index=df.index)
    return combined_df_to_interaction_table(
        combined=combined,
        table_list=table_list,
        interaction_symbol=interaction_symbol
    )


class Summa(NetworkCombiner):
    """
    SUMMA algorithm for combining results.

    Attributes:
        interaction_symbol (str): symbol used to indicate
            interactions in the index of the dataframe.
        name (str): name of the combiner.
        summa_object (pySUMMA.Summa): SUMMA object.
    """

    summa_object = None

    def __init__(self, interaction_symbol='<->', name='summa', **kwargs):
        """
        Instatiate a SUMMA combiner.

        Args:
            interaction_symbol (str, optional): symbol used to indicate
                interactions in the index of the dataframe.
                Defaults to '<->'.
            name (str, optional): name of the combiner. Defaults to 'summa'.
        """
        self.name = name
        self.interaction_symbol = interaction_symbol
        self.summa_object = _summa()
        self.tol = kwargs.get('tol', 1e-3)
        self.max_iter = kwargs.get('max_iter', 500)
        super().__init__(**kwargs)

    def _combine(self, results_list):
        """
        Apply the combination method via SUMMA and assign it to the graph.

        Args:
            results_list (list): a list of InteractionTable objects.
        """
        if len(results_list) == 1:
            logger.warning(
                'One interaction table passed no consensus applied.'
            )
            combined_table = results_list[0]
        else:
            logger.debug('Start combining')
            df = concatenate_intensities(results_list)
            data = df.rank(ascending=False,
                           method='first').apply(fill_na_ranks,
                                                 axis=0).values.T.astype(int)
            self.summa_object.fit(data, tol=self.tol, max_iter=self.max_iter)
            scores = self.summa_object.get_scores(data)
            scores -= scores.min()
            scores /= scores.max()
            combined = pd.Series(scores, index=df.index)
            combined_table = combined_df_to_interaction_table(
                combined=combined,
                table_list=results_list,
                interaction_symbol=self.interaction_symbol
            )
            logger.debug('Finished combining')
        self.graph = combined_table.to_graph()
        logger.debug('Graph computed')

    def __str__(self):
        """
        Get the name of the combiner.

        Returns:
            str: name of the combiner.
        """
        return self.name
