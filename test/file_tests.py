import sys
sys.path.append('../')

import pngcompressor
import unittest
import tempfile
import shutil
import os

FIXTURES = {
    'large png': 'python-logo-large.png',
    'small png': 'python-logo-small.png',
    'large gif': 'python-logo-large.gif',
    'small gif': 'python-logo-small.gif',
    'animation': 'python-logo-animated.gif',
    }
FIXTURES_DIR = './fixtures'

class FileTests(unittest.TestCase):

    def setUp(self):
        self.tmp_path = tempfile.mkdtemp()
        for path in os.listdir(FIXTURES_DIR):
            shutil.copy(os.path.join(FIXTURES_DIR, path), self.tmp_path)
            new_path = os.path.join(self.tmp_path, path)
            assert os.access(new_path, os.F_OK & os.R_OK & os.W_OK)

    def tearDown(self):
        shutil.rmtree(self.tmp_path, True)

    def name_to_png(self, path):
        name, ext = os.path.splitext(path)
        return '%s.png' % name

    def get_tmp_file(self, key):
        return os.path.join(self.tmp_path, self.name_to_png(FIXTURES[key]))

    def get_file(self, key):
        return os.path.join(FIXTURES_DIR, FIXTURES[key])

    def wait(self, job):
        """
        Wait for job thread to end, otherwise the tests will fail
        and the directories will be removed before the compression
        is run.
        """
        job.join()

    def test_compress_single_png(self):
        compressor = pngcompressor.compress(self.get_tmp_file('large png'))
        self.wait(compressor)

        old_file_size = os.path.getsize(self.get_file('large png'))
        new_file_size = os.path.getsize(self.get_tmp_file('large png'))
        
        self.assertTrue(old_file_size > new_file_size)

    def test_compress_single_gif(self):
        compressor = pngcompressor.compress(self.get_tmp_file('large gif'))
        self.wait(compressor)

        old_file_size = os.path.getsize(self.get_file('large gif'))
        new_file_size = os.path.getsize(self.get_tmp_file('large gif'))
        
        self.assertTrue(old_file_size > new_file_size)

    def test_compress_directory(self):
        before_sizes = [os.path.getsize(os.path.join(self.tmp_path, path)) for path in os.listdir(self.tmp_path)
                        if os.path.isfile(os.path.join(self.tmp_path, path))]
        
        compressor = pngcompressor.compress(self.tmp_path)
        self.wait(compressor)
        
        after_sizes = [os.path.getsize(os.path.join(self.tmp_path, path)) for path in os.listdir(self.tmp_path)
                        if os.path.isfile(os.path.join(self.tmp_path, path))]
        
        self.assertNotEqual(before_sizes, after_sizes)

    def test_bypass_png(self):
        compressor = pngcompressor.compress(self.get_tmp_file('small png'))
        self.wait(compressor)

        self.assertFalse(os.path.isfile(self.get_tmp_file('large png')))

    def test_bypass_gif(self):
        raise Exception("Not implemented")

    def test_bypass_animated_gif(self):
        compressor = pngcompressor.compress(self.get_tmp_file('animation'))
        self.wait(compressor)

        self.assertFalse(os.path.isfile(self.get_tmp_file('animation')))
