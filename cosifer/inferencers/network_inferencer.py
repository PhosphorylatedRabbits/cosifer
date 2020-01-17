"""NetworkInferencer abstract interface."""
import logging
from ..handlers.network_handler import NetworkHandler

logger = logging.getLogger(__name__.split('.')[-1])


class NetworkInferencer(NetworkHandler):
    """
    Network inferencer interface.

    Attributes:
        graph (cosifer.collections.graph,Graph): graph representing the
            network.
        trained (bool): flag to indicate whether the inference has been
            performed.
    """
    graph = None
    trained = False

    def __init__(self, **kwargs):
        """Initialize the network inferencer."""
        super().__init__(**kwargs)

    def infer_network(self, data):
        """
        Infer the network.

        Args:
            data (pd.DataFrame): data to be used for the inference.
        """
        if self.trained:
            logger.info('{} already trained'.format(self))
        else:
            logger.info('{} not trained yet. infer.'.format(self))
            self._infer_network(data)
            self.trained = True
            self.dump()

    def _infer_network(self, data):
        """
        Infer the network.

        Args:
            data (pd.DataFrame): data to be used for the inference.
        """
        raise NotImplementedError
