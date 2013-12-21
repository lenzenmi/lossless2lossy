import unittest
import os
import shutil

from .. import lossless2lossy
from .. import flac
from .. import mp3
from .. import sync


class Test_Lossless2lossy(unittest.TestCase):
    testdir = os.path.abspath(os.path.dirname(__file__))
    resources = os.path.join(testdir, 'resources')
    srcdir = os.path.join(resources, 'srcdir')
    destdir = os.path.join(resources, 'destdir')
    mp3file = os.path.join(resources, r'mp3/silence_16_44100_id3v11_id3v23.mp3')
    flacfile = os.path.join(resources, r'flac/silence_16_44100.flac')
    album_art_dir = os.path.join(resources, 'album_art')
    artfile = os.path.join(album_art_dir, r'folder.jpg')
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
            artfile = os.path.join(album, 'folder.jpg')
            shutil.copyfile(self.artfile, artfile)

            return ([artist, album], r_tracks, artfile)

        self.s_new = mkalbum(name='new', path=self.srcdir, file=self.flacfile, tracks=5)
        self.s_new2 = mkalbum(name='new2', path=self.srcdir, file=self.flacfile, tracks=3)
        self.s_mp3 = mkalbum(name='mp3', path=self.srcdir, file=self.mp3file, tracks=8)
        self.d_deleted = mkalbum(name='deleted', path=self.destdir, file=self.flacfile, tracks=5)

        self.sync_obj = sync.Sync(self.srcdir, self.destdir, mp3.Mp3)

    def tearDown(self):
        shutil.rmtree(self.srcdir)
        shutil.rmtree(self.destdir)

    def test_Worker_copy(self):
        worker = lossless2lossy.Worker(self.sync_obj, delete=False)
        mp3file = self.s_mp3[1][0]
        mp3file = self.sync_obj.load_file(mp3file)

        expected_dst = self.sync_obj.src_to_dest(mp3file)
        src, dst, lossy = worker.copy(mp3file)

        self.assertEqual(mp3file.filename, src, 'src files should match')
        self.assertEqual(expected_dst, dst, 'dst files should match')
        self.assertTrue(os.path.isfile(lossy), 'file should have been copied')

    def test_Worker_encode(self):
        worker = lossless2lossy.Worker(self.sync_obj, delete=False)
        flacfile = self.s_new[1][0]
        flacfile = self.sync_obj.load_file(flacfile)

        dst, encoded = worker.encode(flacfile)

        self.assertIsInstance(encoded, mp3.Mp3, 'encoded file should be an MP3')
        self.assertTrue(os.path.isfile(dst), 'encoded file should exist on the filesystem')

    def test_Worker_delete_files(self):
        worker = lossless2lossy.Worker(self.sync_obj, delete=False)
        flacfile = self.d_deleted[1][0]

        dst = worker.delete_files(flacfile)

        self.assertFalse(os.path.isfile(dst), 'file should be removed from the filesystem')

    def test_Worker_delete_subs(self):
        worker = lossless2lossy.Worker(self.sync_obj, delete=False)
        album = self.d_deleted[0][1]

        dst = worker.delete_subs(album)

        self.assertFalse(os.path.isdir(dst), 'folder should be removed from the filesystem')

    def test_Worker_run(self):
        worker = lossless2lossy.Worker(self.sync_obj, delete=True)
        self.assertRaises(SystemExit, worker.run)  # should exit when finished

        # files removed from the source should be deleted
        self.assertFalse(os.path.isdir(self.d_deleted[0][0]))

        # all flac files should be converted to mp3
        # all mp3 and art files should be copied
        s_art = [self.s_new[2], self.s_new2[2], self.s_mp3[2]]
        # Change the source directory to the destination directory
        d_new = [name.replace(self.srcdir, self.destdir) for name in self.s_new[1]]
        d_new2 = [name.replace(self.srcdir, self.destdir) for name in self.s_new2[1]]
        d_mp3 = [name.replace(self.srcdir, self.destdir) for name in self.s_mp3[1]]
        d_art = [name.replace(self.srcdir, self.destdir) for name in s_art]
        # replace file extensions to .mp3
        d_new = [name.replace('.flac', '.mp3') for name in d_new]
        d_new2 = [name.replace('.flac', '.mp3') for name in d_new2]

        for folder in (d_new, d_new2, d_mp3, d_art):
            for file_ in folder:
                self.assertTrue(os.path.isfile(file_), "files should exist")
        '''
        |-- destdir
        |   |-- artist-mp3
        |   |   `-- album-mp3
        |   |       |-- 00 track.mp3
        |   |       |-- 01 track.mp3
        |   |       |-- 02 track.mp3
        |   |       |-- 03 track.mp3
        |   |       |-- 04 track.mp3
        |   |       |-- 05 track.mp3
        |   |       |-- 06 track.mp3
        |   |       |-- 07 track.mp3
        |   |       `-- folder.jpg
        |   |-- artist-new
        |   |   `-- album-new
        |   |       |-- 00 track.mp3
        |   |       |-- 01 track.mp3
        |   |       |-- 02 track.mp3
        |   |       |-- 03 track.mp3
        |   |       |-- 04 track.mp3
        |   |       `-- folder.jpg
        |   `-- artist-new2
        |       `-- album-new2
        |           |-- 00 track.mp3
        |           |-- 01 track.mp3
        |           |-- 02 track.mp3
        |           `-- folder.jpg
        '''

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
