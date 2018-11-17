######################################################################
# class for working directly with images
######################################################################

import logging

log = logging.getLogger(__name__)

import os, subprocess, io, tempfile
from PIL import ImageOps, Image as PILImage, ImageDraw as PILImageDraw
import json

import settings
import utils_fs, utils_exif


class MissingImage(Exception):
    pass
    # log.exception(Exception.message)


class InvalidImage(Exception):
    pass
    # log.exception(Exception.message)


"""
> request for image, including size params
* generate name of image, to check if exists in the cache
    * filename_createdate_longestedge.jpg
? does it exist in the cache? if so then load, if not then create (and save for future)
"""


def get_jpeg_binary(full_path, longest_edge_res):
    format = 'jpeg'
    quality = 50

    _, extension = os.path.splitext(full_path)
    extension = extension[1:]

    # If the image format is CR2, then use exiftool to extract an embedded jpeg image
    if extension.lower() == 'cr2':

        tempdir = tempfile.gettempdir() + os.path.sep
        f, _ = os.path.splitext(os.path.basename(full_path))
        tempf = os.path.join(tempdir, f + ".jpg")

        cmd = '"' + settings.EXIFTOOL + '" -previewimage -b "' + full_path + '" > "' + tempf + '"'
        log.debug("EXIFTOOL cmd: %s" % cmd)

        try:
            subprocess.check_output(cmd, shell=True)
            im = PILImage.open(tempf)
        except subprocess.CalledProcessError as e:
            log.debug(e.output)
            im = PILImage.new('RGB', (30, 30), color='grey')
        except IOError as e:
            log.error(e)
            im = PILImage.new('RGB', (30, 30), color='grey')

        if os.path.exists(tempf):
            os.remove(tempf)

    elif extension.lower() in ('mov', 'mp4'):
        # TODO: support getting framegrab from video files

        tempdir = tempfile.gettempdir() + os.path.sep
        f, _ = os.path.splitext(os.path.basename(full_path))
        tempf = os.path.join(tempdir, f + ".jpg")

        cmd = '"' + settings.FFMPEG + '" -y -i "' + full_path + '" -ss 00:00:01 -vframes 1 "' + tempf + '"'
        log.debug("FFMPEG cmd: %s" % cmd)

        try:
            subprocess.check_output(cmd, shell=True)
            im = PILImage.open(tempf)
        except subprocess.CalledProcessError as e:
            log.debug(e.output)
            im = PILImage.new('RGB', (30, 30), color='grey')
        except IOError as e:
            log.error(e)
            im = PILImage.new('RGB', (30, 30), color='grey')

        if os.path.exists(tempf):
            os.remove(tempf)

    else:
        im = PILImage.open(full_path)

    # rotate the image, if there's orientation metadata
    metadata = utils_exif.get_metadata_batch([full_path])[0]
    if "EXIF:Orientation" in metadata.keys():
        if metadata["EXIF:Orientation"] == 3:
            im = im.rotate(180, expand=True)
        elif metadata["EXIF:Orientation"] == 6:
            im = im.rotate(270, expand=True)
        elif metadata["EXIF:Orientation"] == 8:
            im = im.rotate(90, expand=True)

    # start resizing image
    if im.size[0] > im.size[1]:
        r = float(longest_edge_res) / im.size[0]
        h = int(im.size[1] * r)
        w = longest_edge_res
    else:
        r = float(longest_edge_res) / im.size[1]
        w = int(im.size[0] * r)
        h = longest_edge_res

    # if target w or h > current width or height, then reset w and h
    # if w > im.size[0] or h > im.size[1]:
    #    w = im.size[0]
    #    h = im.size[1]

    # scale iage
    im = im.resize((w, h), PILImage.ANTIALIAS)

    # Write the file contents out to a specific format, but just in memory.
    # Return the file obj

    binary = io.BytesIO()
    im.save(binary, format=format, quality=quality)

    binary.seek(0)

    return binary


class Image(object):
    """
    Most of this class was borrowed from GitHub. I can't find the original repository since, and so haven't given
    proper credit here yet!
    """

    def __init__(self, path, params={}):
        self.path = path
        self.quality = 75
        self.params = params

    def _get_pretty_params_string(self, params):
        """
        Used to convert JSON parameters into a string suitable to make part of a file name
        """
        s = json.dumps(params, ensure_ascii=True)
        chars_to_remove = ['{', '}', ' ', '"', "'"]
        for char in chars_to_remove:
            s = s.replace(char, '')

        chars_to_replace = [':', ',']
        for char in chars_to_replace:
            s = s.replace(char, '-')
        return s

    def _get_cache_path(self):
        # generate cache file name
        cache_name = '%s-%s-%s.jpg' % (
            utils_fs.get_basename(self.path),
            utils_fs.get_creation_date(self.path).replace(':', '-'),
            self._get_pretty_params_string(self.params))

        cache_name = cache_name.replace(':', '-')
        cache_name = cache_name.replace(' ', '-')

        if not os.path.exists(settings.IMAGE_CACHE_PATH):
            os.makedirs(settings.IMAGE_CACHE_PATH)

        return os.path.join(settings.IMAGE_CACHE_PATH, cache_name)

    def scale(self, w, h):
        if w > self.im.size[0]:
            w = self.im.size[0]

        if h > self.im.size[1]:
            h = self.im.size[1]

        self.im = self.im.resize((w, h), PILImage.ANTIALIAS)

    def scale_to_width(self, w):
        r = float(w) / self.im.size[0]
        h = int(self.im.size[1] * r)
        self.scale(w, h)

    def scale_to_height(self, h):
        r = float(h) / self.im.size[1]
        w = int(self.im.size[0] * r)
        self.scale(w, h)

    def crop(self, w=None, h=None):
        w = w or self.im.size[0]
        h = h or self.im.size[1]

        if w > self.im.size[0]:
            w = self.im.size[0]

        if h > self.im.size[1]:
            h = self.im.size[1]

        left = (self.im.size[0] / 2) - (w / 2)
        top = (self.im.size[1] / 2) - (h / 2)
        right = left + w
        bottom = top + h

        self.im = self.im.crop((left, top, right, bottom))

    def zoom_crop(self, w=None, h=None, left=None, top=None):
        if (w is None and h is None) or left is None or top is None:
            raise Exception('Zoom crop requires at least width or height and both left and top')

        w = int(float(w)) if w is not None else int(float(h))
        h = int(float(h)) if h is not None else int(float(w))

        left = int(float(left))
        top = int(float(top))

        right = left + w
        bottom = top + h

        self.im = self.im.crop((left, top, right, bottom))

    def process(self):

        options = self.params

        # First do all the scaling operations
        if 'w' in options and 'h' in options:
            # scale both width and height
            self.scale(int(options['w']), int(options['h']))
        elif 'w' in options:
            # scale width to w, and height proportionally
            self.scale_to_width(int(options['w']))
        elif 'h' in options:
            # scale height to h, and width proportionally
            self.scale_to_height(int(options['h']))
        elif 'le' in options:
            # scale long edge to le, and short edge proportionally
            # if width > height, long edge = width
            if self.im.size[0] > self.im.size[1]:
                self.scale_to_width(int(options['le']))
            else:
                self.scale_to_height(int(options['le']))

        # Now do any cropping.  This order is important.
        if 'cw' in options and 'ch' in options:
            self.crop(w=int(options['cw']), h=int(options['ch']))
        elif 'cw' in options:
            self.crop(w=int(options['cw']))
        elif 'ch' in options:
            self.crop(h=int(options['ch']))

        # Now do any zoom cropping.
        if any(option in options for option in ['zcw', 'zch', 'zct', 'zcl']):
            self.zoom_crop(w=options.get('zcw'),
                           h=options.get('zch'),
                           top=options.get('zct'),
                           left=options.get('zcl'))

        # Post-scaling operations
        if 'pw' in options and 'ph' in options:
            # scale both width and height
            self.scale(int(options['pw']), int(options['ph']))
        elif 'pw' in options:
            # scale width to w, and height proportionally
            self.scale_to_width(int(options['pw']))
        elif 'ph' in options:
            # scale height to h, and width proportionally
            self.scale_to_height(int(options['ph']))

        # Other filters
        if 'gray' in options:
            self.im = ImageOps.grayscale(self.im)

    @property
    def cached_file_exists(self):
        cache_path = self._get_cache_path()
        return utils_fs.isfile(cache_path)

    @property
    def binary(self):

        if self.cached_file_exists:
            self.im = PILImage.open(self._get_cache_path())
            self.fmt = "jpeg"
        else:
            # Browsers like a image/jpeg content-type but not image/jpg.
            # Pillow wants a format that's like 'jpeg', 'gif', 'png', or 'bmp'
            _, extension = os.path.splitext(self.path)
            self.fmt = extension[1:]
            if self.fmt.lower() == 'jpg':
                self.fmt = 'jpeg'
            # If the image format is CR2, then try and use exiftool to extract an embedded jpeg image
            if self.fmt.lower() == 'cr2':
                tempdir = tempfile.gettempdir() + os.path.sep
                f, _ = os.path.splitext(os.path.basename(self.path))
                tempf = os.path.join(tempdir, f + ".jpg")
                try:
                    cmd = '"' + settings.EXIFTOOL + '" -previewimage -b "' + self.path + '" > "' + tempf + '"'
                    log.debug("EXIFTOOL cmd: %s" % cmd)
                    subprocess.check_output(cmd, shell=True)
                    self.im = PILImage.open(tempf)
                    if os.path.exists(tempf):
                        pass
                        os.remove(tempf)
                    self.fmt = 'jpeg'
                except IOError:
                    raise MissingImage("No file for %s" % self.path)
            elif self.fmt.lower() in ('mov', 'mp4'):
                # TODO: support getting framegrab from video files
                # ffmpeg -i input.mp4 -ss 00:00:04 -vframes 1 output.png
                self.im = PILImage.new('RGB', (30, 30), color='grey')
                self.fmt = 'jpeg'
            else:
                self.im = PILImage.open(self.path)

            # TODO support getting orientation from original file
            metadata = utils_exif.get_metadata_batch([self.path])[0]
            if "EXIF:Orientation" in metadata.keys():
                if metadata["EXIF:Orientation"] == 3:
                    self.im = self.im.rotate(180, expand=True)
                elif metadata["EXIF:Orientation"] == 6:
                    self.im = self.im.rotate(270, expand=True)
                elif metadata["EXIF:Orientation"] == 8:
                    self.im = self.im.rotate(90, expand=True)
            # print json.dumps(utils_exif.get_metadata_batch([self.path])[0], sort_keys=True, indent=4)

            self.process()
            if self.params != {}:
                self.im.save(self._get_cache_path(), self.fmt, quality=self.quality)

        # Write the file contents out to a specific format, but just in memory.
        # Return the file obj
        f = io.BytesIO()
        self.im.save(f, self.fmt, quality=self.quality)
        f.seek(0)
        return f

    @property
    def mimetype(self, fmt=None):
        fmt = fmt or self.fmt
        return "image/" + fmt