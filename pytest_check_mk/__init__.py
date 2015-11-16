from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


class MissingFileError(Exception):

    def __init__(self, path):
        message = 'Required file "{}" does not exist.'.format(path)
        super(MissingFileError, self).__init__(message)
