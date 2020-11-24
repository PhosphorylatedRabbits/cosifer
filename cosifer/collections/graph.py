"""Graph class."""
import scipy
import logging
import numpy as np
import pandas as pd
import scipy.sparse as ss
from packaging import version

logger = logging.getLogger(__name__.split('.')[-1])

ADVANCED_INDEXING = version.parse(scipy.__version__) >= version.parse('1.3.0')
SPARSE_MATRIX = ss.csr_matrix
EPSILON = np.finfo(float).eps

if ADVANCED_INDEXING:
    def _scale_graph(graph, i, j, min_value, max_value):
        """Scale sparse graph adjacency in-place"""
        graph[i[:, np.newaxis], j] = (
            graph[i[:, np.newaxis], j] - min_value + EPSILON
        ) / (max_value - min_value + EPSILON)
else:
    def _scale_graph(graph, i, j, min_value, max_value):
        """Scale sparse graph adjacency in-place"""
        graph[i, j] = (
            graph[i, j] - min_value + EPSILON
        ) / (max_value - min_value + EPSILON)


class Graph(object):
    """
    Lightweight class for handling cosifer graph objects.
    If the graph is undirected the adjacency matrix is stored as a sparse
    lower triangular matrix.

    Attributes:
        n (int): number of nodes.
        labels_to_indices (pd.Series): label to index mapping.
        indices_to_labels (pd.Series): index to lable mapping.
        adjacency (spicy.sparse.csr_matrix): sparse adjacency.
        undirected (bool): flag indicating whether edges are directed.
    """
    n = 0
    labels_to_indices = None
    indices_to_labels = None

    def __init__(self, adjacency, labels=None, undirected=True):
        """
        Instantiate a graph.

        Args:
            adjacency (spicy.sparse.csr_matrix): adjacency matrix.
            labels (iterable, optional): node labels. Defaults to None.
            undirected (bool, optional): flag indicating whether edges are
                directed. Defaults to True.

        Raises:
            RuntimeError: raise an error in case the adjacency type is not
                compatible.
        """
        self.undirected = undirected
        if labels is not None:
            self.set_labels(labels)
            self.n = len(labels)
        if isinstance(adjacency, np.ndarray):
            self.set_adjacency_from_numpy(adjacency)
        elif isinstance(adjacency, pd.DataFrame):
            self.set_adjacency_from_pandas(adjacency)
        elif ss.issparse(adjacency):
            self.set_adjacency_from_sparse(adjacency.tolil())
        else:
            logger.error('input adjacency type not compatible.')
            raise RuntimeError('input adjacency type not compatible.')

    def set_labels(self, labels):
        """
        Set the node labels.

        Args:
            labels (iterable): labels to set.

        Raises:
            RuntimeError: in case of inconsitenties between
                the labels and the graph nodes.
        """
        if self.n and self.n != len(labels):
            logger.error(
                'labels and adjacency matrix are ' +
                'inconsistent when setting labels.'
            )
            raise RuntimeError(
                'labels and adjacency matrix are ' +
                'inconsistent when setting labels.'
            )
        # NOTE: fixing labels to be strings to ease their handling
        labels = [str(label) for label in labels]
        self.labels_to_indices = pd.Series(
            {label: index
             for index, label in enumerate(labels)}
        )
        self.indices_to_labels = pd.Series(labels)

    def set_adjacency_from_numpy(self, adjacency):
        """
        Set the adjacency from a numpy ndarray.

        Args:
            adjacency (np.ndarray): adjacency matrix.

        Raises:
            RuntimeError: in case of inconsitencies in the sizes.
        """
        n = adjacency.shape[0]
        if self.n:
            if self.n != n:
                logger.error(
                    'labels and adjacency matrix from ' +
                    'numpy.ndarray are inconsistent.'
                )
                raise RuntimeError(
                    'labels and adjacency matrix from ' +
                    'numpy.ndarray are inconsistent.'
                )
        else:
            labels = [str(index) for index in range(adjacency.shape[0])]
            self.set_labels(labels)
            self.n = n
        if self.undirected:
            adjacency[np.triu_indices(n)] = 0.0
        self.adjacency = SPARSE_MATRIX(adjacency)
        del (adjacency)

    def set_adjacency_from_pandas(self, adjacency):
        """
        Set the adjacency from a pandas dataframe.

        Args:
            adjacency (pd.DataFrame): adjacency matrix.

        Raises:
            RuntimeError: in case of inconsitencies in the sizes.
        """
        n = adjacency.shape[0]
        if self.n:
            if self.n != n:
                logger.error(
                    'labels and adjacency matrix from ' +
                    'pandas.DataFrame are inconsistent.'
                )
                raise RuntimeError(
                    'labels and adjacency matrix from ' +
                    'pandas.DataFrame are inconsistent.'
                )
        else:
            labels = adjacency.columns
            self.set_labels(labels)
            self.n = n
        if self.undirected:
            adjacency.values[np.triu_indices(n)] = 0.0
        self.adjacency = SPARSE_MATRIX(adjacency.values)
        del (adjacency)

    def set_adjacency_from_sparse(self, adjacency):
        """
        Set the adjacency from a sparse matrix.

        Args:
            adjacency (spicy.sparse.csr_matrix): adjacency matrix.

        Raises:
            RuntimeError: in case of inconsitencies in the sizes.
        """
        n = adjacency.shape[0]
        if self.n:
            if self.n != n:
                logger.error(
                    'labels and adjacency matrix from ' +
                    'scipy sparse matrix are inconsistent.'
                )
                raise RuntimeError(
                    'labels and adjacency matrix from ' +
                    'scipy sparse matrix  are inconsistent.'
                )
        else:
            labels = [str(index) for index in range(adjacency.shape[0])]
            self.set_labels(labels)
            self.n = n
        if self.undirected:
            adjacency[np.triu_indices(n)] = 0.0
        self.adjacency = adjacency.tocsr()
        del (adjacency)

    def __str__(self):
        """
        String representation for a graph.

        Returns:
            str: the graph as a string.
        """
        return 'cosifer.collections.graph.Graph\n{}\n{}'.format(
            self.labels_to_indices, self.adjacency
        )

    def __getitem__(self, item):
        """
        Get weight for a pair of labels.

        Args:
            item (tuple or str): a tuple of labels or a single label
                to access the adjacency by row.

        Returns:
            float or np.ndarray: an edge weight or a row of edge weights.
        """
        try:
            a_label, another_label = item
            return self.adjacency[self.labels_to_indices[a_label], self.
                                  labels_to_indices[another_label]]
        except Exception as exc:
            logger.debug('accessing adjacency matrix row.')
            logger.debug(exc)
            return self.adjacency[self.labels_to_indices[item], :]

    def get_scaled_adjacency(self):
        """
        Get a min-max scaled version of the adjacency.

        Returns:
            spicy.sparse.csr_matrix: the min-max scaled adjacency.
        """
        scaled_graph = np.abs(self.adjacency)
        i, j = scaled_graph.nonzero()
        min_value, max_value = (
            scaled_graph[i, j].min(), scaled_graph[i, j].max()
        )
        _scale_graph(scaled_graph, i, j, min_value, max_value)
        return scaled_graph

    def to_interaction_table(self, scaled=True, interaction_symbol='<->'):
        """
        Convert the graph to an interaction table.

        Args:
            scaled (bool, optional): flag to activate min-max scaling of the
                edges. Defaults to True.
            interaction_symbol (str, optional): symbol to depict interactions
                between labels. Defaults to '<->'.

        Returns:
            InteractionTable: the table containing the interactions reported in
                the graph.
        """
        from .interaction_table import InteractionTable
        if self.n < 1:
            # graph is empty
            df = pd.DataFrame(columns=['e1', 'e2', 'intensity'])
        else:
            # graph is not empty
            if scaled:
                coo = self.get_scaled_adjacency().tocoo()
            else:
                coo = self.adjacency.tocoo()

            n = coo.nnz
            labels = np.concatenate(
                [
                    self.indices_to_labels[coo.row].values.reshape(n, 1),
                    self.indices_to_labels[coo.col].values.reshape(n, 1)
                ],
                axis=1
            )

            if self.undirected:
                labels.sort(axis=1)

            df = pd.DataFrame(
                {
                    'e1': labels[:, 0],
                    'e2': labels[:, 1],
                    'intensity': coo.data
                },
                index=[
                    '{}{}{}'.format(e1, interaction_symbol, e2)
                    for e1, e2 in zip(labels[:, 0], labels[:, 1])
                ]
            )

        return InteractionTable(
            df=df,
            interaction_symbol=interaction_symbol,
            labels=list(self.indices_to_labels.values)
        )
