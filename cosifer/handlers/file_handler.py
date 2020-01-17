"""FileHandler interface."""
import logging

logger = logging.getLogger(__name__.split('.')[-1])


class FileHandler(object):
    """FileHandler interface class."""

    def __init__(self, **kwargs):
        """Initialize a FileHandler."""
        pass

    def load(self):
        """Load object from the file."""
        raise NotImplementedError

    def dump(self, buffer):
        """
        Dump object to the file.

        Args:
            buffer (object): a buffer-like object.
        """
        raise NotImplementedError

    def exist(self):
        """Check whether the file exists."""
        raise NotImplementedError
