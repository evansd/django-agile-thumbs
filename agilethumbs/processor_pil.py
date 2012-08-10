from __future__ import division
import re

# Try to import PIL in either of the two ways it can end up installed.
try:
        from PIL import Image, ImageOps
except ImportError:
        import Image, ImageOps

from agilethumbs import ImageProcessorError


def simple_resize(
        infile, outfile, extension,
        width=None, height=None, resize='fit', background='transparent',
        quality=85):
    im = Image.open(infile)
    im = im.convert('RGB')
    # Scale image so it does not exceed specified dimensions
    if resize == 'fit':
        if width is not None or height is not None:
            if width is None:
                width = int(round(im.size[0] * height / im.size[1]))
            elif height is None:
                height = int(round(im.size[1] * width / im.size[0]))
            im.thumbnail((width, height), Image.ANTIALIAS)
    # Scale and crop image so it exactly fills specified dimensions 
    elif resize == 'fill':
        im = ImageOps.fit(im, (width, height), Image.ANTIALIAS)
    # Scale image so it does not exceed specified dimensions and then pad with
    # background color so it exactly fills specified dimensions
    elif resize == 'pad':
        im.thumbnail((width, height), Image.ANTIALIAS)
        tmp = Image.new('RGBA', (width, height), color_from_string(background))
        tmp.paste(im, ((width - im.size[0]) // 2, (height - im.size[1]) // 2))
        im = tmp
    # Scale image to exact dimensions ignoring aspect ratio
    elif resize == 'squash':
        im = im.resize((width, height), Image.ANTIALIAS)
    else:
        raise ImageProcessorError('Unknwon resize option: %s' % resize)
    # Convert `extension` argument into something PIL is happy with
    im_format = extension.encode('ascii').upper()
    if im_format == 'JPG':
                im_format = 'JPEG'
    im.save(outfile, im_format, quality=quality)


color_regex = re.compile('^#' + ('([a-fA-F0-9]{2})' * 3) + '$')

def color_from_string(s):
        if s == 'transparent':
                return (0, 0, 0, 0)
        match = color_regex.match(s)
        if match:
                return tuple([int('0x' + i, 16) for i in match.groups()] + [255])
        else:
                raise ImageProcessorError('Invalid color string: %s' % s)

                      
        
