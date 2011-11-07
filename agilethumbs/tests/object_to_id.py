import tempfile
import shutil

from django.test import TestCase
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
try:
    from django.test.utils import override_settings
except ImportError:
    from agilethumbs.tests.utils import override_settings

from agilethumbs.base import object_to_id, id_to_object

@override_settings()
class TestObjectToID(TestCase):
    
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.tmp_dir
    
    def testFileRoundTrip(self):
        # Create a file using the default storage backend and open it to get a
        # file object
        contents = 'Test content'
        name = default_storage.save('test', ContentFile(contents))
        fileobj = default_storage.open(name)
        fileobj.close()
        # Convert it to an id and back again
        file_id = object_to_id(fileobj)
        newobj = id_to_object(file_id)
        # Check that the resulting object has the same contents as the original
        try:
            self.assertEqual(contents, newobj.read())
        finally:
            newobj.close()
    
    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        
