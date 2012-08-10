import os
import errno
import subprocess

from agilethumbs import ImageProcessorError

CONVERT_PATH = 'convert'


def simple_resize(infile, outfile, extension,
                  width='', height='', resize='fit', background='transparent',
                  quality=85):
    args = []
    # Scale image so it does not exceed specified dimensions
    if resize == 'fit':
        if width != '' or height != '':
            args.extend([
                '-thumbnail', '%sx%s' % (width, height),
            ])
    # Scale and crop image so it exactly fills specified dimensions 
    elif resize == 'fill':
        args.extend([
            '-thumbnail', '%sx%s^' % (width, height),
            '-gravity', 'center',
            '-extent',  '%sx%s' % (width, height)
        ])
    # Scale image so it does not exceed specified dimensions and then pad with
    # background color so it exactly fills specified dimensions
    elif resize == 'pad':
        args.extend([
            '-thumbnail', '%sx%s' % (width, height),
            '-background', background,
            '-gravity', 'center',
            '-extent',  '%sx%s' % (width, height)
        ])
    else:
        raise ImageProcessorError('Unknwon resize option: %s' % resize)
    args.extend([
        '-colorspace', 'sRGB',
        '-quality', str(quality),
    ])
    # Perform conversion
    convert(infile, outfile, extension, args)


def convert(infile, outfile, extension, convert_args):
    # Construct the argument list for convert
    cmd_args = ([CONVERT_PATH, string_arg_from_file(infile)]
                + convert_args
                + ['%s:-' % extension])
    # Invoke convert via subprocess
    try:
        proc = subprocess.Popen(cmd_args, shell=False, stdin=infile,
            stdout=outfile, stderr=subprocess.PIPE)
    except OSError as e:
        if e.errno == errno.ENOENT:
            raise ImageProcessorError(
                "Couldn't find the 'convert' binary.\n"
                "Is ImageMagick installed? (Try 'apt-get install"
                    " imagemagick' on Debian/Ubuntu)\n"
                "If it is installed, make sure 'convert' is somewhere on your"
                    " PATH, or fiddle with %s.CONVERT_PATH" % __name__)
        else:
            raise 
    stderr = proc.communicate()[1]
    if proc.returncode != 0:
        raise ImageProcessorError('ImageMagick error: %s' % stderr)


def string_arg_from_file(fileobj):
    # Get the file extension from the name, if it has a name attribute.
    # ImageMagick can usually determine the format without it, but it helps
    # in some cases.
    try:
        name = fileobj.name
        ext = os.path.splitext(name)[1].lstrip('.')
    except AttributeError:
        ext = ''
    return  (ext + ':-') if ext != '' else '-'

