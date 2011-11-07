import os
import tempfile
import shutil
from StringIO import StringIO

from django.test import TestCase
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.template import Template, Context
try:
    from django.test.utils import override_settings
except ImportError:
    from agilethumbs.tests.utils import override_settings

from agilethumbs import image_url

URL_PREFIX = 'agilethumbs'

urlpatterns = patterns('',
    url(r'^%s/' % URL_PREFIX, include('agilethumbs.urls')),
)


# The actual test settings are configured dynamically in the setUp() method
# but using this decorator ensures they are reset once the tests are run
@override_settings()
class TestImageRequest(TestCase):
    
    urls = __name__
    
    def setUp(self):
        self.contents = 'blah blah blah'
        self.fileobj = StringIO(self.contents)
        self.file_id = u'contains/sub/dirs'
        self.processor_kwargs = {'test': 123, 'other': 'yes'}
        self.extension = 'jpg'
        self.tmp_dir = tempfile.mkdtemp()
        settings.AGILETHUMBS_CACHE_DIR = self.tmp_dir
        settings.AGILETHUMBS_OBJECT_TO_ID = self.object_to_id
        settings.AGILETHUMBS_ID_TO_OBJECT = self.id_to_object
        settings.AGILETHUMBS_STYLES = {
            'test': (self.image_processor, self.extension, 1,
                     self.processor_kwargs)
        }
    
    def object_to_id(self, fileobj):
        self.assertIs(fileobj, self.fileobj)
        return self.file_id
    
    def id_to_object(self, file_id):
        self.assertEqual(file_id, self.file_id)
        return self.fileobj
    
    def image_processor(self, infile, outfile, extension, **kwargs):
        self.assertEqual(kwargs, self.processor_kwargs)
        self.assertEqual(extension, self.extension)
        contents = infile.read()
        outfile.write(contents)
    
    def testRequest(self):
        url = image_url(self.fileobj, 'test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.contents)
        cache_path = os.path.join(self.tmp_dir, url[len('/%s/' % URL_PREFIX):])
        if not os.path.exists(cache_path):
            self.fail('Processed image was not cached')
        with open(cache_path, 'rb') as f:
            self.assertEqual(f.read(), self.contents)
    
    def testTemplateTag(self):
        url = image_url(self.fileobj, 'test')
        template = Template("{% load agilethumbs %}"
                            "{% image_url fileobj 'test'%}")
        tag_url = template.render(Context({'fileobj': self.fileobj}))
        self.assertEqual(url, tag_url)
    
    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
    

