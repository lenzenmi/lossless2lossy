import argparse
import os
import sys
import shutil
import multiprocessing
import functools
from  concurrent.futures import ThreadPoolExecutor as Executor

from . import sync
from . import mp3
from . import abstract


class Worker:

    def __init__(self, sync_obj, delete=False):
        self.sync_obj = sync_obj
        self.delete = delete
        self.encode_class = sync_obj.encode_class
        self.executor = Executor(
                            max_workers=multiprocessing.cpu_count()
                        )
        self.printlock = multiprocessing.Lock()

    def copy(self, job):
        '''
        Copies a file to a new location as determined by
        sync.Sync.src_to_dest()

        :Args:
            * jobs(FileClass)): a FileClass object

        :Returns:
            * src: original path to the file
            * dst: path to the copied file
            * lossy_file_coppied: None or the path to the
                last lossless file copied.
        '''
        lossy_file_coppied = None
        src = job.filename
        dst = self.sync_obj.src_to_dest(src)
        dst_dir = os.path.dirname(dst)

        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)

        shutil.copyfile(src, dst)

        if isinstance(job, abstract.Lossy):
            lossy_file_coppied = dst
        return (src, dst, lossy_file_coppied)

    def encode(self, job):
        '''
        Encodes each file in jobs to a lossy format.

        :Args:
            * jobs(Lossless): an object that inherits from
                abstract.Lossless
        :Returns:
            * dst(str): filename of the encoded file
            * encoded(Lossy): Lossy class object representing the encoded
                file
        '''
        lossless_file = job
        src = lossless_file.filename
        dst = self.sync_obj.src_to_dest(src)
        pcm = lossless_file.decode()
        encoded = self.encode_class.encode(dst, pcm)
        # copy tags
        for tag in lossless_file:
            if tag in encoded.VALID_TAGS:
                encoded[tag] = lossless_file[tag]
        encoded.save()
        return (dst, encoded)

    def post_encode_hook(self, lossy):
        '''
        Runs the post_encode_hook method on *lossy*

        :Args:
            * lossy(Lossy): an object that inherits from
                abstract.Lossy
        '''
        def replaygain_callback(result, folder=None):
            # check for exception
            result.result()
            with self.printlock:
                print('ReplayGain:"{}/"\n'.format(folder))

        folder = os.path.dirname(lossy.filename)
        callback = functools.partial(replaygain_callback, folder=folder)
        task = self.executor.submit(lossy.post_encode_hook)
        task.add_done_callback(callback)

    def delete_files(self, job):
        '''
        Deletes files from the filesystem.

        :Args:
            * job(str): absolute path to the file
        :Returns:
            * str: path to the deleted file
        '''
        file_ = job
        if os.path.isfile(file_):
            os.unlink(file_)
            return file_

    def delete_subs(self, job):
        '''
        Recursively deletes directories and all contents.

        :Args:
            * jobs(str): absolute path to the folder
        :Returns:
            * sub_dir(str): path to the folder that was deleted
        '''
        sub_dir = job
        if os.path.isdir(sub_dir):
            shutil.rmtree(sub_dir)
            return sub_dir

    def run(self):
        '''
        Runs the program
        '''
        compare = self.sync_obj
        not_in_dest = compare.not_in_destination()
        total_files_encoded = 0
        total_files_copied = 0

        try:
            for subdir in not_in_dest:
                copy_jobs = []
                encode_jobs = []
                loaded_file_classes = sync.Sync.load_cls_objs(subdir)
                for file_ in loaded_file_classes:
                    # Only encode lossless files. Lossy files and album art are
                    # copied.
                    if isinstance(file_, abstract.Lossless):
                        encode_jobs.append(file_)
                    else:
                        copy_jobs.append(file_)

                if copy_jobs:
                    lossy_copied = False
                    for copy_job in copy_jobs:
                        __, dst, lossy = self.copy(copy_job)
                        with self.printlock:
                            print('Copied: "{}"\n'.format(dst))
                        if (not lossy_copied) and (lossy):
                            lossy_copied = lossy
                        total_files_copied += 1
                    if lossy_copied:
                        lossy_file = sync.Sync.load_file(lossy_copied)
                        self.post_encode_hook(lossy_file)

                if encode_jobs:
                    executor_futures = []
                    for encode_job in encode_jobs:
                        executor_futures.append(
                            self.executor.submit(self.encode, encode_job)
                        )

                    # Wait for all encode jobs to finish before
                    # post_encode_hook
                    for job in executor_futures:
                        result = job.result()
                        with self.printlock:
                            print('Encoded: {}\n'.format(result[0]))
                        total_files_encoded += 1
                        last_encoded_file = result[1]

                    self.post_encode_hook(last_encoded_file)

            # Wait for all threads to finish
            self.executor.shutdown(wait=True)

            if (self.delete is True):
                # Look for files that have been deleted from the source folder
                not_in_source = compare.not_in_source()
                for subs, files in not_in_source:
                    if subs:
                        for sub in subs:
                            result = self.delete_subs(sub)
                            with self.printlock:
                                print('Deleted: "{}"/\n'.format(result))
                    if files:
                        for file_ in files:
                            result = self.delete_files(file_)
                            with self.printlock:
                                print('Deleted: "{}"\n'.format(result))

        except Exception as e:
            print('** Encountered an Error **')
            print(e)
            sys.exit(1)

        print('** All operations completed successfully **')
        print('\n\tFiles Encoded: {}'.format(total_files_encoded))
        print('\tFiles Copied: {}\n'.format(total_files_copied))

        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description='Encodes lossless files to lossy files.'
    )
    parser.add_argument('--delete',
                        action='store_true',
                        default=False,
                        help=('deletes all files in the encoded folder that'
                              ' no longer exist in the source folder')
                        )
    parser.add_argument('lossyFormat',
                        choices=['mp3'],
                        default='mp3',
                        nargs='?',
                        help='lossy file format')
    parser.add_argument('source',
                        nargs=1,
                        help='source folder containing lossless files')
    parser.add_argument('encoded',
                        nargs=1,
                        help='destination folder where the lossy files '
                             'will go')

    args = parser.parse_args()

    lossy_map = {'mp3': mp3.Mp3}
    lossy_class = lossy_map[args.lossyFormat]

    try:
        compare = sync.Sync(args.source[0], args.encoded[0], lossy_class)
    except Exception as e:
        parser.error(e)

    worker = Worker(compare, args.delete)
    worker.run()

if __name__ == '__main__':
    main()
