"""NetworkHandler interface."""
import os
import logging
import pandas as pd
from ..collections.interaction_table import InteractionTable
from .fs_handler import FileSystemHandler

logger = logging.getLogger(__name__.split('.')[-1])


class NetworkHandler(FileSystemHandler):
    """
    NetwrokHandler interface.

    Attributes:
        graph (cosifer.collections.graph,Graph): graph representing the
            network.
        trained (bool): flag to indicate whether the inference has been
            performed.
        filepath (str): path to the file where the graph is stored.
        parameters (dict): parameters for the inferencer.
    """
    graph = None
    trained = False
    filepath = None

    def __init__(self, filepath=None, **kwargs):
        """
        Initialize the NetworkHandler.

        Args:
            filepath (str, optional): path to the file where the graph is
                stored. Defaults to None.
        """
        self.parameters = kwargs
        self.filepath = filepath

    def dump(
        self,
        scaled=True,
        interaction_symbol='<->',
        threshold=None,
        compression='gzip'
    ):
        """
        Dump graph to the file.

        Args:
            scaled (bool, optional): flag to activate min-max scaling of the
                edges. Defaults to True.
            interaction_symbol (str, optional): symbol to depict interactions
                between labels. Defaults to '<->'.
            threshold (float, optional): threshold to apply to the intensity.
                Defaults to None.
            compression (str, optional): compression type. Defaults to 'gzip'.
        """
        if (self.trained and self.filepath and self.graph is not None):
            logger.info('{} dump to file'.format(self))
            if self.graph.adjacency.size > 0:
                interactions = self.graph.to_interaction_table(
                    scaled=scaled, interaction_symbol=interaction_symbol
                )
                try:
                    os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
                    interactions.df.to_csv(
                        self.filepath, compression=compression
                    )
                    del (interactions)
                except Exception as exc:
                    logger.info('cannot write file {}'.format(self.filepath))
                    logger.info(str(exc))
                logger.info('{} dumped'.format(self))
            else:
                logger.warning('{} no interactions, cannot dump'.format(self))
        else:
            logger.warn('network not dumped for {}'.format(self))

    def load(self, compression='gzip'):
        """
        Load graph from the file.

        Argd:
            compression (str, optional): compression type. Defaults to 'gzip'.
        """
        logger.info('{} try to load inferred network from file'.format(self))
        if os.path.isfile(self.filepath):
            inference_results = pd.read_csv(
                self.filepath, header=0, index_col=0, compression=compression
            )
            interactions = InteractionTable(df=inference_results)
            self.graph = interactions.to_graph()
            self.trained = True
            del (interactions)
            logger.info('{} loaded from file'.format(self))
        else:
            logger.info('{} no existing file found'.format(self))
