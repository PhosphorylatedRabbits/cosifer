"""FileSystemHandler inferencer."""
import logging
import os
from .file_handler import FileHandler

logger = logging.getLogger(__name__.split('.')[-1])


class FileSystemHandler(FileHandler):
    """
    FileSystemHandler inferencer.

    Attributes:
        filepath (str): path to the file.
    """
    filepath = None

    def __init__(self, filepath, **kwargs):
        """
        Initialize FileSystemHandler inferencer.

        Args:
            filepath (str): path to the file.
        """
        self.filepath = filepath
        super(FileSystemHandler, self).__init__(**kwargs)

    def load(self, file_type='r'):
        """
        Load object from the file.

        Argd:
            file_type (str, optional): type of the file. Defaults to 'r'.

        Returns:
            IOBase: the loaded file.
        """
        logger.info('try to read file: {}'.format(self.filepath))
        if os.path.isfile(self.filepath):
            return open(self.filepath, file_type)
        else:
            logger.info('file does not exist')

    def dump(self, buffer, file_type='w'):
        """
        Dump object to the file.

        Args:
            buffer (object): a buffer-like object.
            file_type (str, optional): type of the file. Defaults to 'w'.
        """
        logger.info('dump to file {}'.format(self.filepath))
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, file_type) as f:
                f.write(buffer)
        except Exception as exc:
            logger.info('cannot write to file {}'.format(self.filepath))
            logger.info(str(exc))

    def exist(self):
        """
        Check whether the file exists.

        Returns:
            bool: true if the file exists, false otherwise.
        """
        return os.path.isfile(self.filepath)

    def __str__(self):
        """
        Get a string representation for the handler.

        Returns:
            str: string representation for the handler.
        """
        return 'file://{}'.format(self.filepath)
