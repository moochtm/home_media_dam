
import logging
log = logging.getLogger(__name__)

import os, io

import errno
import settings
import utils_fs


def get_file_binary(filename):

    binary = False
    for path, dirs, files in os.walk(settings.IMAGE_CACHE_PATH):
        for f in files:
            if f == filename:
                full_path = utils_fs.join_path(path, f)
                with open(full_path, 'rb') as file:
                    binary = io.BytesIO(file.read())
    return binary


def store_binary_file(filename, binary, year):

    full_path = os.path.join(settings.IMAGE_CACHE_PATH, year, filename)

    if not os.path.exists(os.path.dirname(full_path)):
        try:
            os.makedirs(os.path.dirname(full_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    binary.seek(0)

    try:
        with open(full_path, 'wb') as f:
            f.write(binary.read())
    except:
        log.error("Error saving file to cache (%s)" % full_path)
    return True


def check_file_exists(filename, year):

    year = str(year)
    full_path = os.path.join(settings.IMAGE_CACHE_PATH, year, filename)
    return os.path.exists(full_path)