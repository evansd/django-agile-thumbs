import os
import errno
from contextlib import contextmanager
from tempfile import mkstemp

from django.conf import settings
from django.http import Http404
from django.core.urlresolvers import get_callable
from django.utils._os import safe_join
from django.views.static import serve as django_serve_static

from agilethumbs.base import unescape, id_to_object, sign_params
from agilethumbs.concurrency import atomic_create


class SignatureMismatchError(Exception):
    pass


def agilethumbs_image(request, **kwargs):
    filename = get_cache_filename(**kwargs)
    # If the file already exists serve it up
    if os.path.exists(filename):
        return serve_file(request, filename)
    # Allow override of id_to_object function in settings
    this_id_to_object = get_callable(getattr(
        settings, 'AGILETHUMBS_ID_TO_OBJECT', id_to_object))
    processor, processor_kwargs, extension = get_image_processor(**kwargs)
    # Create file
    with atomic_create(filename) as outfile:
        fileobj = this_id_to_object(unescape(kwargs['file_id']))
        try:
            processor(fileobj, outfile, extension, **processor_kwargs)
        finally:
            if hasattr(fileobj, 'close') and callable(fileobj.close):
                fileobj.close()
    # Serve it up
    return serve_file(request, filename)


def get_cache_filename(file_id, style, version, signature, extension):
    """
    Return path to cached file for supplied request parameters
    """
    cache_url = '%s-%s-%s-%s.%s' % (file_id, style, version, signature,
                                    extension)
    cache_path = safe_join(settings.AGILETHUMBS_CACHE_DIR, cache_url)
    return cache_path


def get_image_processor(file_id, style, version, signature, extension):
    """
    Validate supplied request parameters and return the relevant image
    processor function, keyword arguments and extension
    
    Raises SignatureMismatchError for invalid signatures or Http404 for valid
    requests which reference outdated style versions.
    """
    # Check the signature
    if signature != sign_params(file_id, style, version, extension):
        raise SignatureMismatchError()
    # Get and check the style details: the valid signature ensures that the
    # details were correct at time of URL generation, but not that they
    # haven't changed since
    try:
        style_config = settings.AGILETHUMBS_STYLES[style]
    except KeyError:
        raise Http404()
    if version != unicode(style_config[2]):
        raise Http404()
    image_processor = get_callable(style_config[0])
    processor_kwargs = style_config[3]
    # Extension should be an str, not unicode, for PIL's sake
    extension = extension.encode('ascii')
    return (image_processor, processor_kwargs, extension)


@contextmanager
def atomic_create(filename, mode=0660, makedirs=True):
    """
    Return a temporary file object to write to and move file into position
    once creation is complete
    """
    directory = os.path.dirname(filename)
    if makedirs:
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    tmp_name = mkstemp(dir=directory)[1]
    tmp_file = open(tmp_name, 'wb')
    try:
        # Yield file handle, actual content creation happens here
        yield tmp_file
        # Set permissions and move it into place
        os.chmod(tmp_name, mode)
        os.rename(tmp_name, filename)
    except:
        os.unlink(tmp_name)
        raise
    finally:
        tmp_file.close()


def serve_file(request, path):
    return django_serve_static(request, path, document_root='/')
    
    
