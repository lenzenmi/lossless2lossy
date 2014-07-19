'''
This class represents an mp3 music file. If the file in question does not have
a .mp3 extension, or mutagenx can not load the file, a TypeError is returned.
'''
import re
import subprocess
import os
import glob

import mutagenx.mp3

from . import abstract


class Mp3(mutagenx.mp3.EasyMP3, abstract.Lossy):
    EXTENSIONS = ('.mp3',)
    TYPE = 'lossy'
    tags = mutagenx.easyid3.EasyID3.valid_keys
    VALID_TAGS = tuple(tags.keys())

    def __init__(self, filename, *args, **kwargs):
        '''
        :Args:
            * filename(string): absolute path to an mp3 file
        :Raises:
            * TypeError: if the file is not an mp3 file
        '''
        pattern = re.compile(r'.*\.mp3$', re.IGNORECASE)
        if re.search(pattern, filename):
            mutagenx.mp3.EasyMP3.__init__(self, filename, *args, **kwargs)
        else:
            raise TypeError('not an mp3 file.')

    @classmethod
    def encode(self, outfile, popen_object):
        '''
        encodes a PCM stream to mp3 -V0

        :Args:
            * outfile(str): output filename. Extensions will be renamed to'
                ' self.EXTENSION
            * popen_object(subprocess.Popen): an object with a PCM data stream'
                ' piped to *popen_object.stdout*
        :Returns:
            * Mp3: class object initiated to the newly encoded file
        :Raises:
            * EXCEPTION: Encoder error
        '''
        dirname = os.path.dirname(outfile)
        filename_without_extension = os.path.splitext(outfile)[0]
        outfile = filename_without_extension + self.EXTENSIONS[0]

        # make directories as needed
        if not os.path.isdir(dirname):
            os.makedirs(dirname, exist_ok=True)

        cmd = ['lame', '-V0', '-', outfile]
        encoded = subprocess.Popen(cmd,
                                   stdin=popen_object.stdout,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        encoded.communicate()
        popen_object.stdout.close()
        if encoded.returncode == 0:
            return Mp3(outfile)
        else:
            raise Exception('lame encoder error')

    def _replaygain_album(self):
        '''
        Calls `mp3gain` to perform an album based analysis on all *.mp3
        files in the current directory.

        :Raises:
            * Exception: mp3gain returned a non 0 exit code
        '''
        path = os.path.dirname(self.filename)
        mp3files = glob.glob(os.path.join(path, '*' + self.EXTENSIONS[0]))
        cmd = ['mp3gain', '-a', '-c', '-s', 'i', '-s', 'r']
        cmd.extend(mp3files)
        popen = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        result = popen.communicate()
        if not popen.returncode == 0:
            raise Exception('mp3gain error', result)

    def _add_v11_tags(self):
        '''
        Calls `eyeD3` to add v1.1 id3 tags to all mp3 files

        :Raises:
            * Exception
        '''
        path = os.path.dirname(self.filename)
        mp3files = glob.glob(os.path.join(path, '*' + self.EXTENSIONS[0]))
        for mp3file in mp3files:
            cmd = ['eyeD3', '--to-v1.1'] + [mp3file]
            popen = subprocess.Popen(cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            result = popen.communicate()
            if not popen.returncode == 0:
                raise Exception('eyeD3 error', result)

    def post_encode_hook(self):
        '''
        Triggers a replaygain on all mp3 files in the directory
        and adds id3v1.1 tags to all mp3 files.
        '''
        self._replaygain_album()
        self._add_v11_tags()
