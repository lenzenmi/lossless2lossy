'''
Created on Dec 23, 2013

@author: mike
'''
import os

from . import abstract


class Art(abstract.FileClass):
    '''
    Class for working with cover-art files.
    Returns an Art object if filename matches a cover-art filename.
    Otherwise raises TypeError.

    Arguments:
        * filename (str): path to file on filesystem

    Raises:
        * TypeError: if file does not exist, or if file name does not match
        known coverart filenames.
    '''
    _NAMES = ('album.gif', 'album.jpg', 'albumartsmall.gif',
             'albumartsmall.jpg', 'cover.gif', 'cover.jpg',
             'folder.gif', 'folder.jpg', 'thumb.gif', 'thumb.jpg')

    def __init__(self, filename):
        self.filename = filename
        valid = True
        basename = os.path.basename(self.filename)

        if (not os.path.isfile(self.filename)
            or basename not in self._NAMES):
            valid = False

        if not valid:
            raise TypeError(
                '\'{}\' is not a valid '
                'album art file'.format(self.filename)
            )
