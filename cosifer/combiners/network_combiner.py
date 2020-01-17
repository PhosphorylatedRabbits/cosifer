"""Interface for a network combiner."""
import logging
from ..handlers.network_handler import NetworkHandler

logger = logging.getLogger(__name__.split('.')[-1])


class NetworkCombiner(NetworkHandler):
    """
    Abstract interface for a network combiner.

    Attributes:
        trained (bool): flag to indicate whether the combiner is
            already trained.
    """

    def combine(self, results_list):
        """
        Apply the combination method. Checking whehter the combiner has been
        already trained.

        Args:
            results_list (list): a list of InteractionTable objects.
        """
        if self.trained:
            logger.info('{} already trained'.format(self))
        else:
            logger.info('{} not trained yet. combine.'.format(self))
            self._combine(results_list)
            self.trained = True
            self.dump()

    def _combine(self, results_list):
        """
        Apply the combination method.

        Args:
            results_list (list): a list of InteractionTable objects.
        """
        pass
