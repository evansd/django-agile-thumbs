import os
import tempfile
import shutil
import subprocess
import re

from django.test import TestCase
from django.conf import settings

from agilethumbs import processor_im, processor_pil

class TestSimpleResizeIM(TestCase):
    
    image_lib = processor_im
    
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.test_img = os.path.join(self.tmp_dir, 'rose.png')
        subprocess.check_call(['convert', 'magick:rose', self.test_img])
    
    def tmpFile(self, name):
        return os.path.join(self.tmp_dir, name)
        
    def assertImageSize(self, filename, size):
        output = subprocess.check_output(
            ['identify', '-format', '%w,%h', filename])
        dimensions = tuple(map(int, output.split(',')))
        self.assertEqual(dimensions, size)
    
    def assertImageFormat(self, filename, extension):
        output = subprocess.check_output(
            ['identify', '-format', '%m', filename])
        self.assertEqual(output.strip().lower(), extension)
    
    def doResize(self, extension, **kwargs):
        outname = tempfile.mkstemp(dir=self.tmp_dir)[1]
        with open(self.test_img, 'rb') as orig, open(outname, 'wb') as outfile:
            self.image_lib.simple_resize(orig, outfile, extension, **kwargs)
        return outname
    
    def testFitWidth(self):
        outfile = self.doResize('jpg', resize='fit', width=40)
        self.assertImageSize(outfile, (40, 26))
    
    def testFitHeight(self):
        outfile = self.doResize('jpg', resize='fit', height=30)
        self.assertImageSize(outfile, (46, 30))
    
    def testFitBoth(self):
        outfile = self.doResize('jpg', resize='fit', width=35, height=35)
        self.assertImageSize(outfile, (35, 23))
    
    def testFill(self):
        outfile = self.doResize('jpg', resize='fill', width=30, height=30)
        self.assertImageSize(outfile, (30, 30))
    
    # TODO: Test "pad" resize method (use ImageMagick compare script)
        
    def testFormatConvert(self):
        for ext in ['jpeg', 'png', 'gif', 'tiff']:
            outfile = self.doResize(ext)
            self.assertImageSize(outfile, (70, 46))
            self.assertImageFormat(outfile, ext)
    
    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

class TestSimpleResizePIL(TestSimpleResizeIM):
    image_lib = processor_pil

