'''
Created on Dec 19, 2013

@author: mike
'''
import os
import re

from . import flac
from . import mp3
from . import art
from . import abstract


class Sync:
    '''
    A class for listing differences and similarities between two directories
    on the file system.
    '''
    _FILE_CLASSES = (flac.Flac, mp3.Mp3, art.Art)

    def __init__(self, srcdir, destdir, encode_class):
        self.srcdir = self.validate_path(srcdir)
        self.destdir = self.validate_path(destdir)
        if self.destdir.startswith(self.srcdir):
            raise Exception('"{}" is inside of "{}" ...'
                            .format(self.destdir, self.srcdir))

        self.encode_class = encode_class
        if not issubclass(self.encode_class, abstract.Lossy):
            raise Exception('encode_class must inherit from abstract.Lossy')
        self.encode_class_extension = encode_class.EXTENSIONS[0]
        self.lossless_extensions = []
        for class_ in self._FILE_CLASSES:
            if getattr(class_, 'TYPE', None) == 'lossless':
                self.lossless_extensions.extend(class_.EXTENSIONS)

    def validate_path(self, path):
        '''
        Converts a given path to a directory to an absolute path.

        :Args:
            * path(str): path to a directory
        :Returns:
            * str: absolute path to the directory
        :Raises:
            * Exception: not a valid path on the filesystem
        '''
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.isdir(path):
            return path
        else:
            raise Exception('\'{}\' is not a valid path'.format(path))

    def src_to_dest(self, path):
        '''
        Converts a path pointing to a file or folder in the source folder
        to a equivalent path in the destination folder.

        :Args:
            * path
                + str: a path pointing to a directory or folder in the
                source folder
                + FileClass: an object representing a music or art file
        :Returns:
            * str: a path pointing to the same object in the destination
                folder. This path may or may not exist.
        :Raises:
            * Exception: path is not in the source folder
        '''
        if hasattr(path, 'filename'):
            path = path.filename

        s_root = self.srcdir
        d_root = self.destdir
        encoded_extension = self.encode_class_extension

        if not path.startswith(s_root):
            raise Exception('\'{}\' not in source path {}'
                            .format(path, s_root))

        new_path = os.path.join(d_root, path[len(s_root):].lstrip('/'))

        if os.path.isdir(path):
            return new_path

        if os.path.isfile(path):
            base, ext = os.path.splitext(new_path)
            if ext in self.lossless_extensions:
                return base + encoded_extension

        return new_path

    def dest_to_src(self, path):
        '''
        Converts a path in the destination folder to a tuple of possible paths
        in the source folder. These paths may or may not exist. A tuple is
        returned because the file extensions of lossless files are changed when
        converting to lossy formats and the original file extensions are not
        known.

        :Args:
            * path(str): a path pointing to a directory or folder in the
                source folder
        :Returns:
            * tuple(str): a tuple of possible path names in the source folder
                that would produce ``path`` in the destination folder
        :Raises:
            * Exception: path not in the destination folder
        '''
        source_root = self.srcdir
        destination_root = self.destdir

        if not path.startswith(destination_root):
            raise Exception('\'{}\' not in destination path \'{}\''
                            .format(path, destination_root))

        lossless_file_extensions = self.lossless_extensions
        lossy_encoded_file_extension = self.encode_class_extension

        new_path = os.path.join(source_root,
                                path[len(destination_root):].lstrip('/'))

        if os.path.isdir(path):
            return (new_path,)

        if os.path.isfile(path):
            base, ext = os.path.splitext(new_path)
            new_path = [new_path]
            if ext == lossy_encoded_file_extension:
                for extension in lossless_file_extensions:
                    new_path.append(base + extension)

            return tuple(new_path)

    def not_in_destination(self):
        '''
        all files in the source folder that are not in the destination folder
        or that have newer mtimes than in the destination folder.
        Each iteration searches a new subdirectory of the source folder.

        :Returns:
            * tuple(str): a list of filenames in the source directory that
                are either not present in the destination folder, or have
                modification times older than those in the source directory.
        '''
        walker = os.walk(self.srcdir)

        for root, __, files in walker:
            source_files = []
            files_not_in_dest = []

            for file in files:
                absolute_path = os.path.join(root, file)
                source_files.append(absolute_path)

            for s_file in source_files:
                destination_file = self.src_to_dest(s_file)
                if not os.path.isfile(destination_file):
                    files_not_in_dest.append(s_file)
                else:  # if source file has been modified
                    if (os.path.getmtime(s_file)
                        > os.path.getmtime(destination_file)):
                        files_not_in_dest.append(s_file)

            if files_not_in_dest:
                yield tuple(files_not_in_dest)

    def not_in_source(self):
        '''
        Produces a touple of directories and files in the destination folder
        that are not in the source folder. Each iteration represents a new
        folder in the source directory.

        :Returns:
            * generator(tuple(str([subs])), tuple(str([files])): a tuple of
                paths pointing to subdirectories and files in the destination
                folder but not in the source folder
        '''
        walker = os.walk(self.destdir)

        for root, subs, files in walker:
            subs_not_in_src = []
            files_not_in_src = []

            if subs:
                for sub in subs:
                    sub_abs_path = os.path.join(root, sub)
                    if not os.path.isdir(
                        self.dest_to_src(sub_abs_path)[0]
                    ):
                        subs_not_in_src.append(sub_abs_path)

            if files:
                for file in files:
                    file_abs_path = os.path.join(root, file)
                    file_dir = os.path.dirname(file_abs_path)
                    src_dir = self.dest_to_src(file_dir)[0]
                    file_exists = False

                    if os.path.isdir(src_dir):
                        possible_files = self.dest_to_src(file_abs_path)
                        if possible_files:
                            possible_base_ext = (os.path.splitext(pf)
                                                 for pf in possible_files)
                            src_files = (os.path.join(src_dir, f)
                                         for f in os.listdir(src_dir))
                            source_file_base_ext = [os.path.splitext(p)
                                                    for p in src_files]
                            # Test if possible source file exits using a
                            # case insensitive file extension
                            for p_base, p_ext in possible_base_ext:
                                for sf_base, sf_ext in source_file_base_ext:
                                    if (sf_base == p_base
                                        and re.search(p_ext,
                                                      sf_ext,
                                                      re.IGNORECASE)):
                                        file_exists = True

                    if not file_exists:
                        files_not_in_src.append(file_abs_path)
            if (subs_not_in_src) or (files_not_in_src):
                yield (tuple(subs_not_in_src), tuple(files_not_in_src))

    @classmethod
    def load_cls_objs(self, paths):
        '''
        Returns a list of FileClass objects representing the files passed in.
        Files that cannot be loaded as FileClass objects are ignored.

        :Args:
            * paths(iter(str)): an iterable that produces path names pointing
                to files
        :Returns:
            * list(FileClass): a list of FileClass objects representing the
                files in ``paths``
        '''
        opened_files = []

        for file_ in paths:
            for file_class in self._FILE_CLASSES:
                try:
                    opened_file = file_class(file_)
                    opened_files.append(opened_file)
                except Exception:
                    pass
        return opened_files

    @classmethod
    def load_file(self, path):
        path = self.load_cls_objs([path])
        return path[0]
