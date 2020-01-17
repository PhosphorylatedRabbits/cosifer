"""Interation table class."""
import logging
import numpy as np
import pandas as pd
import scipy.sparse as ss

logger = logging.getLogger(__name__.split('.')[-1])

interaction_table_columns = {'e1', 'e2', 'intensity'}
extreme_separator = '@&+*+&@'


class InteractionTable(object):
    """
    Interaction table class representation of an edge list.

    Attributes:
        df (pd.DataFrame): underlying dataframe containing the edge list.
        labels (iterable): node labels.
    """

    def __init__(
        self,
        df=pd.DataFrame(columns=list(interaction_table_columns)),
        labels=None,
        interaction_symbol=None,
        force_undirected=False
    ):
        """
        Initialize an InteractionTable.

        Args:
            df (pd.DataFrame, optional): pandas DataFrame table.
                Defaults to an empty table.
            labels (iterable): nodes labels.
            interaction_symbol (str): interaction symbol for indexing.
            force_undirected: specify if the loaded table represent an
               undirected graph. Defaults to False.

        Raises:
            RuntimeError: in case of columns inconsistencies.
        """
        if interaction_table_columns.issubset(df.columns.values.tolist()):
            # NOTE: fixing labels to be strings to ease their handling
            df['e1'] = df['e1'].astype(str)
            df['e2'] = df['e2'].astype(str)
            self.df = df
            if force_undirected:
                self.df = directed_to_undirected_interactions(self.df)
            e1 = self.df['e1'].values.tolist()
            e2 = self.df['e2'].values.tolist()
            if interaction_symbol:
                self.df.index = [
                    '{}{}{}'.format(i, interaction_symbol, j)
                    for i, j in zip(e1, e2)
                ]
            self.df = self.df[self.df['intensity'] != 0.]
            self.labels = (
                labels
                if labels else sorted(list(set(e1) | set(e2)))
            )
            # NOTE: fixing labels to be strings to ease their handling
            self.labels = [str(label) for label in self.labels]
        else:
            logger.error('inconsistent columns in pandas.DataFrame')
            raise RuntimeError('inconsistent columns in pandas.DataFrame')

    def to_graph(self, undirected=True, imposed_labels=None):
        """
        Get a graph from the stored edges.

        Args:
            undirected (bool, optional): flag to indicate whether the
                interactions are undirected. Defaults to True.
            imposed_labels (iterable, optional): node label to consider.
                Defaults to None.

        Returns:
            Graph: a graph.
        """
        from .graph import Graph
        # Check for directionality. Crucial for storing in a
        # lower triangular sparse matrix, the graph.
        labels = None
        if imposed_labels is None:
            labels = (
                sorted(self.labels, reverse=True)
                if undirected else self.labels
            )
        else:
            # NOTE: making sure labels imposed are strings
            labels = (
                sorted(map(str, imposed_labels), reverse=True)
                if undirected else imposed_labels
            )
        n = len(labels)
        labels_to_indices = pd.Series(
            {label: index
             for index, label in enumerate(labels)}
        )
        row = labels_to_indices[self.df['e1']].values
        col = labels_to_indices[self.df['e2']].values
        values = self.df['intensity'].values
        adjacency = ss.coo_matrix((values, (row, col)), shape=(n, n))
        return Graph(adjacency=adjacency, labels=labels)

    def apply_filter(
        self,
        labels=None,
        prune_labels=True,
        indices=None,
        threshold=0.0,
        top_n=None
    ):
        """
        Apply a filter to get an InteractionTable.

        Args:
            labels (iterable, optional): node labels to select.
                Defaults to None.
            prune_labels (bool, optional): prune labels not present in the
                final table. Defaults to True.
            indices (itarable, optional): indices to filter rows.
                Defaults to None.
            threshold (float, optional): threshold for the edge weights.
                Defaults to 0.0.
            top_n (int, optional): number of top interactions to keep.
                Defaults to None.

        Returns:
            InteractionTable: a filtered interaction table.
        """
        df = self.df.copy()
        df_labels = self.labels.copy()
        if indices is not None:
            df = df.loc[indices]
        if labels is not None:
            selected = [
                index for index, row in df.iterrows()
                if row['e1'] in labels and row['e2'] in labels
            ]
            df = df.loc[selected]
            if prune_labels:
                df_labels = sorted(list(set(df['e1']) | set(df['e2'])))
        if threshold > 0.0:
            df = df[df['intensity'] >= threshold]
        if top_n is not None:
            df = df.sort_values(ascending=False, by='intensity')[:top_n]
        return InteractionTable(df=df, labels=df_labels)

    def get_df_dict(self, threshold=None):
        """
        Get a dictionary to represent the edge list.

        Args:
            threshold (float, optional): threshold to filter edge by
                intensity. Defaults to None.

        Returns:
            dict: a dictionary representing then edge list dataframe.
        """
        return self.df[np.abs(self.df['intensity']) > threshold
                       ].to_dict() if threshold else self.df.to_dict()

    def __str__(self):
        """
        String representation for an InteractionTable.

        Returns:
            str: the string representing the interactions table.
        """
        return (
            'cosifer.collections.interactions_table.' +
            'InteractionsTable\n{}\n{}'.format(self.labels, self.df)
        )

    def to_edge_list(self, interaction_symbol='<->', weights=True):
        """
        Returns an edge list containing the interactions.

        Args:
            interaction_symbol (str, optional): Symbol separating the labels
                in the index of the edge list dataframe. Defaults to '<->'.
            weights (bool, optional): Flag indicating whether weights are
                returned. Defaults to True.

        Returns:
            list: a list of edges represented by tuples.
        """
        return interaction_table_to_edge_list(
            self, interaction_symbol=interaction_symbol, weights=weights
        )


def process_index(index, intensity, interaction_symbol):
    """
    Process index to get edge tuple. Disregard edge weight.

    Args:
        index (str): index of the edge list dataframe.
        intensity (float): intensity of the edge.
        interaction_symbol (str): symbol used to separate node labels.

    Returns:
        tuple: a tuple containing edge labels.
    """
    return tuple(index.split(interaction_symbol))


def process_index_with_weights(index, intensity, interaction_symbol):
    """
    Process index to get edge tuple including edge weight.

    Args:
        index (str): index of the edge list dataframe.
        intensity (float): intensity of the edge.
        interaction_symbol (str): symbol used to separate node labels.

    Returns:
        tuple: a tuple containing edge labels and weight.
    """
    return tuple(index.split(interaction_symbol) + [intensity])


def interaction_table_to_edge_list(
    interaction_table, interaction_symbol='<->', weights=True
):
    """
    Convert an InteractionTable to an edge list.

    Args:
        interaction_table (InteractionTable): an interaction table.
        interaction_symbol (str, optional): Symbol separating the labels
            in the index of the edge list dataframe. Defaults to '<->'.
        weights (bool, optional): Flag indicating whether weights are
            returned. Defaults to True.

    Returns:
        list: a list of edges represented by tuples.
    """
    process_index_intensity = process_index
    if weights:
        process_index_intensity = process_index_with_weights
    return [
        process_index_intensity(index, intensity, interaction_symbol)
        for index, intensity in
        zip(interaction_table.df.index, interaction_table.df['intensity'])
    ]


def interaction_table_from_dict(interaction_dictionary):
    """
    Construct an InteractionTable from a dictionary.

    Args:
        interaction_dictionary (dict): an interaction dictionary.
            The dictionary should contain two keys: 'labels', containing the
            node labels, and 'interactions', an object that can be used to
            construct a dataframe representing the edge list.

    Returns:
        InteractionTable: the interaction table.
    """
    return InteractionTable(
        df=pd.DataFrame(interaction_dictionary['interactions']),
        labels=interaction_dictionary['labels']
    )


def interaction_table_from_edge_list(interaction_list):
    """
    Construct an InteractionTable from a list.

    Args:
        interaction_list (list): an edge list containing tuples.

    Returns:
        InteractionTable: the interaction table for the provided edge list.
    """
    return InteractionTable(
        pd.DataFrame(
            [[e1, e2, intensity] for e1, e2, intensity in interaction_list],
            columns=['e1', 'e2', 'intensity']
        ),
        interaction_symbol='<->',
        force_undirected=True
    )


def interaction_table_from_gzip(filepath):
    """
    Construct an InteractionTable from a gzipped file containing an edge list.

    Args:
        filepath (str): path to the gipped file.

    Returns:
        InteractionTable: the interaction table from the gzipped edge list.
    """
    edge_list_df = pd.read_csv(
        filepath, header=0, index_col=0, compression='gzip'
    )
    return InteractionTable(df=edge_list_df[['e1', 'e2', 'intensity']])


def process_group(row):
    """
    Process a grouped edge list dataframe

    Args:
        row (pd.Series): a dataframe row.

    Returns:
        list: a list with entitity labels and weight.
    """
    splitted_name = row.name.split(extreme_separator)
    return sorted(splitted_name) + [row[2]]


def directed_to_undirected_interactions(directed_interactions):
    """
    Processing of a directed table, discarding directions and keeping only
    the maximum edge value. It will drop and reindex with integers the table.
    :param: directed_interactions: directed interactions table.
    :return: an undirected version of the given table.

    Args:
        directed_interactions (pd.DataFrame): directed interactions dataframe.

    Returns:
        pd.DataFrame: undirected interactions dataframe
    """
    columns = directed_interactions.columns.tolist()
    directed_interactions['order'] = directed_interactions.apply(
        lambda row: extreme_separator.join(sorted((row[0], row[1]))), axis=1
    )
    directed_interactions = directed_interactions.groupby('order').max()
    undirected_interactions = pd.DataFrame(
        directed_interactions.apply(process_group, axis=1).values.tolist()
    )
    undirected_interactions.columns = columns
    return undirected_interactions
