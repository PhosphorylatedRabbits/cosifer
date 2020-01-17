"""Core combiner utilities."""
import logging
from functools import reduce
import pandas as pd
from ..collections.interaction_table import InteractionTable

logger = logging.getLogger(__name__.split('.')[-1])


def combined_df_to_interaction_table(
    combined, table_list, interaction_symbol='<->'
):
    """
    Transform combined intensities dataframe into an InteractionTable.

    Args:
        combined (pd.DataFrame): combined intensities dataframe.
        table_list (list): a list of InteractionTable objects.
        interaction_symbol (str, optional): symbol used to indicate
            interactions in the index of the dataframe. Defaults to '<->'.

    Returns:
        InteractionTable: an InteractionTable representing the combined
            intensities.
    """
    e1, e2 = zip(
        *[
            tuple(combined_index.split(interaction_symbol))
            for combined_index in combined.index
        ]
    )
    labels = set(
        reduce(lambda a, b: a + b, map(lambda e: e.labels, table_list))
    )
    return InteractionTable(
        pd.DataFrame(
            {
                'e1': e1,
                'e2': e2,
                'intensity': combined
            }, index=combined.index
        ),
        labels=sorted(labels)
    )


def concatenate_intensities(table_list, threshold_rate=None):
    """
    Concatenate intensities from a list of InteractionTable objects.

    Args:
        table_list (list): a list of InteractionTable objects.
        threshold_rate (float, optional): threshold rate for the NAs.
            Defaults to None, a.k.a no threshold applied.

    Returns:
        InteractionTable: an InteractionTable representing the combined
            intensities.
    """
    if threshold_rate:
        return pd.concat(
            (table.df['intensity'] for table in table_list),
            sort=False,
            axis=1
        ).dropna(axis=0, thresh=threshold_rate * len(table_list))
    else:
        return pd.concat(
            (table.df['intensity'] for table in table_list),
            sort=False,
            axis=1
        )
