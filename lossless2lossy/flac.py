'''
Module for working with flac files
'''
import subprocess
import os
import re

import mutagenx.flac

from . import abstract


class Flac(mutagenx.flac.FLAC, abstract.Lossless):
    EXTENSIONS = ('.flac',)
    TYPE = 'lossless'

    def __init__(self, filename):
        pattern = re.compile(r'.*\.flac$', re.IGNORECASE)
        if re.search(pattern, filename):
            mutagenx.flac.FLAC.__init__(self, filename)
        else:
            raise TypeError('not a flac file')

    def decode(self, outfile='-'):
        '''
        Returns a subprocess object with a decoded PCM stream piped to its
        stdout attribute.
        '''
        gopts = ['--single-threaded']
        infile_opts = ['-G', '-b 16']
        outfile_opts = ['rate', '44100', 'dither', '-s']
        cmd = (['sox'] + gopts + infile_opts + [self.filename]
               + ['-t', 'wav', outfile] + outfile_opts)

        popen = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        return popen
