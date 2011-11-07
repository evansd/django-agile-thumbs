Django Agile Thumbs
===================

A lightweight, loosely-coupled Django app for resizing and processing images. Features include:

 * Images are created on request, rather than during the template rendering stage, so image processing does not block HTML output.
 * Easy to add your own image transformation functions.
 * Easy to add support for any kind of file storage backend -- certainly does not assume that uploaded files are stored under the public web root!
 * URLs include "cache busting" version parameter so images can be safely cached forever by browsers and CDNs.


Requirements
------------

 * Python 2.7
 * Django 1.3
 
and, to use the default image resizing functions, either:

 * Python Imaging Library (PIL) 1.1; or
 * ImageMagick 6.6

(Agile Thumbs may well work on older versions of the above, but has not been tested with them.)

Quick Start
-----------

 1. Grab the code from github and get it on your Python path.
 2. Add `agilethumbs` to your installed apps.
 3. In `settings.py` set `AGILETHUMBS_CACHE_DIR` to some directory in which Django can read and write files and create directories.
 4. In `urls.py` include agilethumbs.urls e.g: `url(r'^thumbnails/', include('agilethumbs.urls')),`
 5. In `settings.py` define some image "styles". If you have ImageMagick installed you can try these settings:
 
        AGILETHUMBS_STYLES = {
            'test': ('agilethumbs.processor_im.simple_resize', 'jpg', 1, {'width': 100}),
        }
    
    Otherwise, if you have Python Imaging Library installed, try these:
    
        AGILETHUMBS_STYLES = {
            'test': ('agilethumbs.processor_pil.simple_resize', 'jpg', 1, {'width': 100}),
        }
 
Basic Usage
-----------

To get the URLs for your images, use the `agilethumbs.image_url` function or, in Django templates, the `{% image_url %}` template tag (add `{% load agilethumbs %}` to your template to access this).

Both have the same usage:

    image_url(django_file_instance, 'image_style_name')
    
Or, for the template tag:

    {% image_url django_file_instance 'image_style_name' %}

Style names are strings which specify what sort of transformation you want to apply.
You define them in an `AGILETHUMBS_STYLES` dictionary in `settings.py`.
Here is the default configuration:

    AGILETHUMBS_STYLES = {
        'default': ('agilethumbs.processors.simple_resize_pil', 'jpg', 1, {'width': 100}),
    }

The style configuration maps style names to tuples with the following values:

 - **Image processing function**: Can be either a string or a callable. See the section on image processing functions for how to define your own.
 - **Image extension**: Extension of the *output* image; the input image can be in any format your image processor understands.
 - **Style version number**: "Cache buster" value; included in the image URLs, so if you change any of the style settings you can change this number and the relevant images will be regenerated next time they are requested.
 - **Keyword arguments**: Passed to the image processing function.

**Note:** style names can only contain alphanumeric characters and underscore.

Image Processors
----------------

Agile Thumbs comes with two image processors: `processor_pil.simple_resize` and `processor_im.simple_resize`.
The both provide the same API, but the former uses the Python Image Library (PIL) and the latter uses ImageMagick (using subprocess to call `convert`).

They take the following arguments:

 - **width**: Width in pixels (optional).
 - **height**: Height in pixels (optional).
 - **resize**: One of 'fit', 'fill', 'pad' (optional, default: 'fit').
   - **'fit'**: Scale the image so that it is a large as possible without exceeding the specified width and/or height.
   - **'fill'**: Scale and crop the image so that it entirely fills the specified width and height.
   - **'pad'**: Like 'fit', but pad the image with background color so that the result entirely fills the specified width and height.
 - **background**: Hex color (e.g, '#00ff00') or 'transparent' (optional -- only makes sense when resize is 'pad').
 - **quality**: Set the compression level for output files (optional, default: 85)

### Defining your own processors

If the default processors don't meet your needs it is very easy to define your own.
An image processor is just a function with the following signature:

    process_image(infile, outfile, extension, [... optional keyword args ...])
    
 - **infile**: File-like object to read original image from.
 - **outfile**: File-like object to write output to.
 - **extension**: Requested image extension (so you know what format to write).
 - ... any keyword arguments supplied in the style definition.

Production Caching Configuration
--------------------------------

Agile Thumbs is designed to be configured so that your webserver (e.g. nginx or Apache) can serve cached files without invoking Python. This involves:

 - Setting AGILETHUMBS_CACHE_DIR to somewhere the webserver can access.
 - Having the webserver check for files in there (either using `try_files` on nginx, or the `-f` mod_rewrite flag on Apache) before passing the request to Django.

Agile Thumbs will use the image URL to determine the path in the cache directory to store the file. For instance, if your `urls.py` file looks like this

    ...
    url('^thumbnails/', include('agilethumbs.urls')),
    ...
    
and a request comes in for `http://example.com/thumbnails/foo/bar.jpg`, it will be cached in `[AGILETHUMBS_CACHE_DIR]/foo/bar.jpg`.

Because the image URLs contain a style version parameter it is safe to set expires headers on them to maximum. This also means you can safely stick a CDN such as Amazon CloudFront in front of your image server.

Dealing with Different File Storage Types
-----------------------------------------

Agile Thumbs is only very loosely coupled to Django's file storage mechanisms. The way it works is this: when a file object is passed to the `image_url` function or template tag it then gets passed to the function specified by `AGILETHUMBS_OBJECT_TO_ID`. This function returns a string which forms part of the resulting URL. When that URL is first requsted, Agile Thumbs extracts the string from the URL and passes it to the function specified by `AGILETHUMBS_ID_TO_OBJECT`. In return, it expects an object that it can pass to the image processing function which will then write out an image.

So, you can pass any sort of object you like into `image_url` as long as you:

 - Define an OBJECT_TO_ID function which transforms that object into a string ID.
 - Define an ID_TO_OBJECT function which transforms that string ID into a file-like object
 - Define an image processing function which tranforms that file-like object into an image.

The OBJECT_TO_ID function can output arbitrary Unicode strings which will be safely escaped for inclusion in the URL. The escaping mechanism preserves slashes (although it encodes multiple slashes) so you divide cached files into sub-directories.

The default function pair only works with locally stored files and is extremely simple: the string ID is just the `name` attribute of the passed in file; and this ID is then passed into `django.core.files.storage.default_storage.open()` to recover the file.


