#!/usr/bin/env python

import sys
import os
import re
import threading

import Image
import ImageSequence

ADDED_TOKEN = '-nq8'
PATTERN_TO_REMOVE = re.compile(ADDED_TOKEN)

def compare_files(file1, file2):
    """
    Compares two files:
    -1 First one is smaller
    0 Both are equal
    1 Second one is smaller
    """
    return cmp(os.path.getsize(file1), os.path.getsize(file2))

def keep_smallest_file(old_path, new_path):
    if not os.path.isfile(old_path):
        return
    if not os.path.isfile(new_path):
        os.rename(old_path, new_path)
    else:
        comparison = compare_files(old_path, new_path)
        if comparison == -1:
            os.rename(old_path, new_path)
        else:
            os.remove(old_path)

def is_animation(path):
    frames = tuple(ImageSequence.Iterator(Image.open(path)))
    return len(frames) > 1

def compress(path):
    if os.path.isdir(path):
        for new_path in os.listdir(path):
            compress(os.path.join(path, new_path))
    job = CompressionJob(path)
    job.start()
    return job

class CompressionJob(threading.Thread):

    def __init__(self, path):
        super(CompressionJob, self).__init__()
        self.path = path

    def run(self):
        path = self.path
        name, ext = os.path.splitext(path)
        if ext == '.png':
            os.system('pngnq -f %s' % path)
            tmp_path = ''.join([name, ADDED_TOKEN, ext])
            keep_smallest_file(tmp_path, path)
        elif ext == '.gif':
            image = Image.open(path)
            if is_animation(path):
                return
            new_path = '%s.png' % name
            try:
                image.save(new_path)
            except Exception as e:
                print 'error trying to save %s as %s: %s' % (path, new_path, e)
                return
            try:
                compress(new_path)
            except Exception as e:
                print 'error trying to compress %s: %s' % (new_path, e)
                return
            if compare_files(path, new_path) == 1:
                os.remove(path)
            else:
                os.remove(new_path)
        

if __name__ == '__main__':
    path = sys.argv[1]
    compress(path)
