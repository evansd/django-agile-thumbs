import re
import hmac
import urllib
from hashlib import sha1
from base64 import b32encode

from django.conf import settings
from django.core.urlresolvers import reverse, get_callable
from django.core.files.storage import default_storage
from django.core.exceptions import ImproperlyConfigured


class ImageProcessorError(Exception):
	pass


def image_url(fileobj, style='default'):
	# Allow override of object_to_id function in settings
	this_object_to_id = get_callable(getattr(
		settings, 'AGILETHUMBS_OBJECT_TO_ID', object_to_id))
	# Get file extension and version number for selected image style
	try:
		extension, version = settings.AGILETHUMBS_STYLES[style][1:3]
	except KeyError:
		raise ImproperlyConfigured("No such image style '%s' defined in "
			"settings.AGILETHUMBS_STYLES" % style)
	except AttributeError:
		raise ImproperlyConfigured("You must define some image styles in "
			"settings.AGILETHUMBS_STYLES.\nSee documentation for examples.")
	file_id = escape(this_object_to_id(fileobj))
	version = unicode(version)
	signature = sign_params(file_id, style, version, extension)
	return reverse('agilethumbs_image', kwargs={
		'file_id': file_id,
		'style': style,
		'version': version,
		'signature': signature,
		'extension': extension
	})


def sign_params(*args):
	msg = '\n'.join(args)
	signature = hmac.new(settings.SECRET_KEY, msg, digestmod=sha1).digest()
	return b32encode(signature).rstrip('=').lower()


def object_to_id(fileobj):
	return fileobj.name

def id_to_object(file_id):
	return default_storage.open(file_id)


slash_regex = re.compile("""
	  ^/      # Leading
	| /$      # Trailing
	| (?<=/)/ # Multiple
	""", re.VERBOSE)

def escape(s):
	enc = s.encode('utf8')
	enc = urllib.quote(enc, safe='/')
	enc = enc.replace('.', '%2E')
	# Encode leading, trailing and multiple slashes
	enc = slash_regex.sub('%2F', enc)
	return enc.replace('%', '~')

def unescape(s):
	return urllib.unquote(s.replace('~', '%')).decode('utf8')
