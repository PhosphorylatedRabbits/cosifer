"""Combiner for interaction tables."""
import logging
from .network_combiner import NetworkCombiner
from .core import concatenate_intensities, combined_df_to_interaction_table

logger = logging.getLogger(__name__.split('.')[-1])


def combine_tables(
    table_list, interaction_symbol='<->',
    processing_concatenated_intensities_fn=lambda x: x,
    reduce_fn=lambda x: x.mean(axis=1),
    **kwargs
):
    """
    Compute the combined intensities from a list of interaction
    tables.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.
        processing_concatenated_intensities_fn (function, optional): function
            to apply on the concatenated intensities. Defaults to identity.
        reduce_fn (function, optional): function to reduce intensities over
            dataframe rows. Defaults to mean.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combined_df_to_interaction_table(
        combined=reduce_fn(
            processing_concatenated_intensities_fn(
                concatenate_intensities(table_list, **kwargs)
            )
        ),
        table_list=table_list,
        interaction_symbol=interaction_symbol
    )


def get_scaled_ranks(dataframe):
    """
    Scaled ranks from an intensity dataframe.

    Args:
        dataframe (pd.DataFrame): intensity dataframe.

    Returns:
        pd.DataFrame: scaled ranks dataframe
    """
    ranks = dataframe.rank()
    return ranks / ranks.max()


def hard_mean_scaled_ranks_table(
    table_list, interaction_symbol='<->', **kwargs
):
    """
    Compute the mean on the scaled ranks without considering interaction
    existence.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol,
        processing_concatenated_intensities_fn=get_scaled_ranks,
        reduce_fn=lambda x: x.sum(axis=1) / len(table_list)
    )


def mean_scaled_ranks_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Compute the mean on the scaled ranks.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol,
        processing_concatenated_intensities_fn=get_scaled_ranks
    )


def median_scaled_ranks_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Compute the median on the scaled ranks.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol,
        processing_concatenated_intensities_fn=get_scaled_ranks,
        reduce_fn=lambda x: x.median(axis=1)
    )


def max_scaled_ranks_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Compute the maximum on the scaled ranks.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol,
        processing_concatenated_intensities_fn=get_scaled_ranks,
        reduce_fn=lambda x: x.max(axis=1)
    )


def min_scaled_ranks_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Compute the minimum on the scaled ranks.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol,
        processing_concatenated_intensities_fn=get_scaled_ranks,
        reduce_fn=lambda x: x.min(axis=1)
    )


def hard_mean_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Compute the mean on the intensities without considering interaction
    existence.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol,
        reduce_fn=lambda x: x.sum(axis=1) / len(table_list)
    )


def mean_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Compute the mean on the intensities.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol
    )


def median_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Compute the median on the intensities.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol,
        reduce_fn=lambda x: x.median(axis=1)
    )


def max_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Compute the maximum on the intensities.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol,
        reduce_fn=lambda x: x.max(axis=1)
    )


def min_table(table_list, interaction_symbol='<->', **kwargs):
    """
    Compute the minimum on the intensities.

    Args:
        table_list (list): a list of interaction tables.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: the combined interaction table.
    """
    return combine_tables(
        table_list, interaction_symbol=interaction_symbol,
        reduce_fn=lambda x: x.min(axis=1)
    )


class CombineInteractionTables(NetworkCombiner):
    """
    Combine interaction tables representing networks using a function.

    Attributes:
        name (str): name of the combiner.
        combine_tables (function): function to combine interaction tables.
        interaction_symbol (str): symbol used to indicate
            interactions in the index of the dataframe.
        graph (cosifer.collections.Graph): combined graph.
    """

    def __init__(
        self,
        combine_tables=mean_table,
        interaction_symbol='<->',
        name='cit',
        **kwargs
    ):
        """
        Initialize the CombineInteractionTables combiner.

        Args:
            combine_tables (function, optional): function to combine
                interaction tables. Defaults to mean combination.
            interaction_symbol (str, optional): symbol used to indicate
                interactions in the index of the dataframe. Defaults to '<->'.
            name (str, optional): name of the combiner. Defaults to 'cit'.
        """
        self.name = name
        self.combine_tables = combine_tables
        self.interaction_symbol = interaction_symbol
        super().__init__(**kwargs)

    def _combine(self, results_list):
        """
        Apply the combination method and assign it to the graph.

        Args:
            results_list (list): a list of InteractionTable objects.
        """
        logger.debug('Start combining')
        combined_table = self.combine_tables(
            results_list, self.interaction_symbol, **self.parameters
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


class WOC(CombineInteractionTables):
    """
    Wisdom Of Crowds implementation.
    """

    def __init__(
        self,
        interaction_symbol='<->',
        name='woc',
        **kwargs
    ):
        """
        Initialize the WOC combiner.

        Args:
            interaction_symbol (str, optional): symbol used to indicate
                interactions in the index of the dataframe. Defaults to '<->'.
            name (str, optional): name of the combiner. Defaults to 'woc'.
        """
        super().__init__(
            combine_tables=mean_scaled_ranks_table,
            interaction_symbol=interaction_symbol,
            name=name,
            **kwargs
        )


class WOCHard(CombineInteractionTables):
    """
    Wisdom Of Crowds with hard mean combiner implementation.
    """

    def __init__(
        self,
        interaction_symbol='<->',
        name='woc_hard',
        **kwargs
    ):
        """
        Initialize the WOCHard combiner.

        Args:
            interaction_symbol (str, optional): symbol used to indicate
                interactions in the index of the dataframe. Defaults to '<->'.
            name (str, optional): name of the combiner. Defaults to 'woc_hard'.
        """
        super().__init__(
            combine_tables=hard_mean_scaled_ranks_table,
            interaction_symbol=interaction_symbol,
            name=name,
            **kwargs
        )
