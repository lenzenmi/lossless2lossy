'''
Created on Dec 19, 2013

@author: mike
'''

import shutil
import unittest
import os
import sys
import time
import glob

from .. import sync
from .. import flac
from .. import mp3
from .. import art

class Test_Sync(unittest.TestCase):
    testdir = os.path.abspath(os.path.dirname(__file__))
    resources = os.path.join(testdir, 'resources')
    srcdir = os.path.join(resources, 'srcdir')
    destdir = os.path.join(resources, 'destdir')
    mp3file = os.path.join(resources, r'mp3/silence_16_44100_id3v11_id3v23.mp3')
    flacfile = os.path.join(resources, r'flac/silence_16_44100.flac')
    album_art_dir = os.path.join(resources, 'album_art')
    flac_dir = os.path.join(resources, 'flac')
    mp3_dir = os.path.join(resources, 'mp3')


    def setUp(self):
        for path in [self.srcdir, self.destdir]:
            os.mkdir(path)

        def mkalbum(name, path, file, tracks):
            artist = os.path.join(path, 'artist-' + name)
            album = os.path.join(artist, 'album-' + name)
            extension = os.path.splitext(file)[1]
            r_tracks = []
            for path in [artist, album]:
                os.mkdir(path)
            for track in range(tracks):
                track = os.path.join(album, '{:02} track{}'.format(track, extension))
                shutil.copyfile(file, track)
                r_tracks.append(track)

            return ([artist, album], r_tracks)

        self.s_new = mkalbum(name='new', path=self.srcdir, file=self.flacfile, tracks=5)

        self.d_modified = mkalbum(name='modified', path=self.destdir, file=self.mp3file, tracks=10)
        time.sleep(.1)  # wait to ensure different mtime
        self.s_modified = mkalbum(name='modified', path=self.srcdir, file=self.flacfile, tracks=10)

        self.d_deleted = mkalbum(name='deleted', path=self.destdir, file=self.mp3file, tracks=15)

        self.s_old = mkalbum(name='old', path=self.srcdir, file=self.flacfile, tracks=5)
        time.sleep(.1)  # wait to ensure different mtime
        self.d_old = mkalbum(name='old', path=self.destdir, file=self.mp3file, tracks=5)

    def tearDown(self):
        shutil.rmtree(self.srcdir)
        shutil.rmtree(self.destdir)

    def test_Sync_validate_path(self):
        s = sync.Sync(self.srcdir, self.destdir, mp3.Mp3)
        self.assertEqual(s.srcdir, self.srcdir)
        self.assertEqual(s.destdir, self.destdir)

        self.assertRaises(Exception, sync.Sync, 'garbage', 'more_garbage')

    def test_Sync_src_to_dest(self):
        s = sync.Sync(self.srcdir, self.destdir, mp3.Mp3)
        srcpath = self.s_old[0][1]
        destpath = self.d_old[0][1]

        self.assertEqual(s.src_to_dest(srcpath), destpath)

    def test_Sync_dest_to_src_reversed(self):
        s = sync.Sync(self.srcdir, self.destdir, mp3.Mp3)
        srcpath = self.d_old[0][1]
        destpath = self.s_old[0][1]

        self.assertIn(destpath, s.dest_to_src(srcpath))

    def test_Sync_src_to_dest_file(self):
        s = sync.Sync(self.srcdir, self.destdir, mp3.Mp3)
        srcfiles = self.s_old[1]
        destpaths = self.d_old[1]

        srcfiles = [flac.Flac(x) for x in srcfiles]

        for index in range(len(srcfiles)):
            self.assertEqual(s.src_to_dest(srcfiles[index]), destpaths[index])

    def test_Sync_not_in_dest(self):
        s = sync.Sync(self.srcdir, self.destdir, mp3.Mp3)
        diff = s.not_in_destination()
        for album_tracks in diff:
            self.assertNotEqual(set(album_tracks), set(self.s_old[1]), 'old album should exist and not be found')
            self.assertIn(set(album_tracks), [set(self.s_new[1]), set(self.s_modified[1])], 'should not exist or should have newer mtime and should be diff')

    def test_Sync_not_in_src(self):
        s = sync.Sync(self.srcdir, self.destdir, mp3.Mp3)
        diff = s.not_in_source()
        for i in diff:
            for folder in i[0]:
                self.assertNotIn(folder, self.d_old[0], 'should exist')
                self.assertNotIn(folder, self.d_modified[0], 'should exist')

                self.assertIn(folder, self.d_deleted[0], 'should not exist')
            if i[1]:
                self.assertNotEqual(set(i[1]), set(self.d_old[1]), 'should exist and not be diff')
                self.assertNotEqual(set(i[1]), set(self.d_modified[1]), 'should exist and not be diff')

                self.assertEqual(set(i[1]), set(self.d_deleted[1]), 'should not exist and should be diff')

    def test_Sync__load_files_flac(self):
        paths = glob.glob(os.path.join(self.flac_dir, '*'))
        opened_files = sync.Sync.load_cls_objs(paths)
        for file in opened_files:
            self.assertIsInstance(file, flac.Flac, 'should load as a flac class')

    def test_Sync__load_files_mp3(self):
        paths = glob.glob(os.path.join(self.mp3_dir, '*'))
        opened_files = sync.Sync.load_cls_objs(paths)
        for file in opened_files:
            self.assertIsInstance(file, mp3.Mp3, 'should load as a mp3 class')

    def test_Sync__load_files_art(self):
        paths = glob.glob(os.path.join(self.album_art_dir, '*'))
        opened_files = sync.Sync.load_cls_objs(paths)
        for file in opened_files:
            self.assertIsInstance(file, art.Art, 'should load as an art class')

    def test_Sync__load_files_nothing(self):
        paths = glob.glob(os.path.join(self.testdir, '*'))
        opened_files = sync.Sync.load_cls_objs(paths)
        self.assertEqual(opened_files, [], 'should be empty')

    def test_Sync_load_file(self):
        path = self.s_new[1][0]
        opened_file = sync.Sync.load_file(path)
        self.assertIsInstance(opened_file, flac.Flac, 'should load as a flac class')

    def test_Sync_same_destDir_and_srcDir(self):
        self.assertRaises(Exception, sync.Sync, self.srcdir, self.srcdir, mp3.Mp3)

    def test_Sync_not_lossy_encoder_class(self):
        self.assertRaises(Exception, sync.Sync, self.srcdir, self.destdir, flac.Flac)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
