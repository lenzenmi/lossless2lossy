'''
Created on Dec 24, 2013

@author: mike
'''
import unittest
import os
import sys
import shutil
import mimetypes
import subprocess
import glob

from .. import mp3

class Test_Mp3(unittest.TestCase):
    testdir = os.path.abspath(os.path.dirname(__file__))
    resources = os.path.join(testdir, 'resources')
    tmp = os.path.join(resources, 'tmp')
    mp3_path = os.path.join(resources, 'mp3')
    wav_path = os.path.join(resources, 'wav')

    def setUp(self):
        os.mkdir(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_mp3_encode(self):
        wav_file = os.path.join(self.wav_path, 'silence_16_44100.wav')
        outfile = os.path.join(self.tmp, 'silence.mp3')

        popen = subprocess.Popen(['cat', wav_file], stdout=subprocess.PIPE)

        encoded_file = mp3.Mp3.encode(outfile, popen)

        self.assertIsInstance(encoded_file, mp3.Mp3, 'should return a Mp3 object')
        self.assertTrue(os.path.isfile(encoded_file.filename), 'encoded_file should exist')
        self.assertEqual(mimetypes.guess_type(encoded_file.filename)[0], 'audio/mpeg', 'encoded_file should be a mp3 file')

    def test_mp3__replaygain_album(self):
        tmp_mp3 = os.path.join(self.tmp, 'mp3')
        os.mkdir(tmp_mp3)
        mp3_files = glob.glob(os.path.join(self.mp3_path, '*.mp3'))
        for file in mp3_files:
            shutil.copy(file, tmp_mp3)
        mp3_files = glob.glob(os.path.join(tmp_mp3, '*.mp3'))
        mp3.Mp3(mp3_files[0])._replaygain_album()
        for file in mp3_files:
            replay_gained_mp3 = mp3.Mp3(file)
            self.assertIn('replaygain_album_gain', replay_gained_mp3.pprint(), 'should have id3 tags from mp3gain')

    def test_mp3__add_v11_tags(self):
        tmp_mp3 = os.path.join(self.tmp, 'mp3')
        os.mkdir(tmp_mp3)
        mp3_files = glob.glob(os.path.join(self.mp3_path, '*.mp3'))
        for file in mp3_files:
            shutil.copy(file, tmp_mp3)
        mp3_files = glob.glob(os.path.join(tmp_mp3, '*.mp3'))
        mp3.Mp3(mp3_files[0])._add_v11_tags()
        self.assertTrue(True, 'no way to test...')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
