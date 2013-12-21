'''
Created on Dec 24, 2013

@author: mike
'''

import unittest
import os
import glob
import sys
import shutil
import mimetypes

from .. import flac

class Test_Flac(unittest.TestCase):
    testdir = os.path.abspath(os.path.dirname(__file__))
    resources = os.path.join(testdir, 'resources')
    tmp = os.path.join(resources, 'tmp')
    flac_path = os.path.join(resources, 'flac')

    def setUp(self):
        os.mkdir(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_flac_decode(self):
        flac_files = glob.glob(os.path.join(self.flac_path, '*'))
        for file in flac_files:
            flac_file = flac.Flac(file)
            out_file = os.path.join(self.tmp, 'flac.wav')
            popen = flac_file.decode(out_file)
            popen.communicate()
            self.assertEqual(popen.returncode, 0, 'sox should exit with 0 return code')
            self.assertTrue(os.path.isfile(out_file), 'out_file should exist')
            self.assertEqual(mimetypes.guess_type(out_file)[0], 'audio/x-wav', 'outfile should be a wav file')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
