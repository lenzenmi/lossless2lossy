'''
Created on Dec 23, 2013

@author: mike
'''

import unittest
import os
import glob
import sys

from .. import art

class Test_Art(unittest.TestCase):
    testdir = os.path.abspath(os.path.dirname(__file__))
    resources = os.path.join(testdir, 'resources')
    album_art = os.path.join(resources, 'album_art')
    flac = os.path.join(resources, 'flac')

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_art_good_files(self):
        art_files = glob.glob(os.path.join(self.album_art, '*'))
        for file in art_files:
            cover = art.Art(file)
            self.assertIn(cover.filename, art_files)

    def test_art_bad_files(self):
        art_files = glob.glob(os.path.join(self.flac, '*'))
        for file in art_files:
            self.assertRaises(TypeError, art.Art, file)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
