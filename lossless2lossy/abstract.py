'''
Module for defining abstract base classes for class objects that represent
files on the file system
'''
import abc


class FileClass(metaclass=abc.ABCMeta):
    'Abstract Base Class for all file type classes'
    @abc.abstractmethod
    def __init__(self, filename):
        '''
        All FileClass subclasses should have an attribute ``self.filename``
        that reports the file's absolute path.
        '''
        self.filename = filename


class Lossless(FileClass):
    '''
    Base class for all Lossless Files.

    ** The EXTENSION constant must be set **
    '''
    EXTENSIONS = ('.wav',)  # Case Insensitive
    TYPE = 'lossless'

    @abc.abstractmethod
    def __init__(self, filename):
        '''
        * Should raise a type error if ``filename`` is not the correct
        file format.
        * Should set the attribute ``self.filename``
        '''
    @abc.abstractmethod
    def decode(self, outfile='-'):
        '''
        * Should return an object with a decoded PCM stream piped to its
        stdout attribute.
        '''


class Lossy(FileClass):
    '''
    Base class for all Lossless Files.

    ** The EXTENSION constant must be set **
    ** VALID_TAGS must be set to a list of tags that the class can accept**
        more information can be found on the
        `mutagenx website
        <http://mutagen.readthedocs.org/en/latest/tutorial.html>_`
    '''
    EXTENSIONS = ('.XXX',)  # The first entry should be used for new encodes
    TYPE = 'lossy'
    VALID_TAGS = (None,)

    @abc.abstractmethod
    def __init__(self, filename):
        '''
        * Should raise a type error if ``filename`` is not the correct
        file format.
        * Should set the attribute ``self.filename``
        '''

    @classmethod
    @abc.abstractmethod
    def encode(self, outfile, popen_object):
        '''
        Encodes a PCM stream. Must be a classmethod

        :Args:
            * outfile(str): output filename. Extensions will be renamed to'
                ' self.EXTENSION
            * popen_object(subprocess.Popen): an object with a PCM data stream'
                ' piped to *popen_object.stdout*
        :Returns:
            * Lossy: class object initiated to the newly encoded file
        :Raises:
            * EXCEPTION: Encoder error
        '''

    @abc.abstractmethod
    def post_encode_hook(self):
        '''
        Triggered once after all files in a directory have been encoded.
        Useful for applying replaygain using album analysis.
        '''
