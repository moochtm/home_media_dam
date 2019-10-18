
# import (1) python built-in, (2) downloaded 3rd party, (3) own

import time, os
from optparse import OptionParser
import inspect
import logging
from logging.handlers import TimedRotatingFileHandler

import src.thirdparty.exiftool as exiftool
et = exiftool.ExifTool()
import src.thirdparty.sortphotos as sortphotos

import settings
from src.api.core import utils_fs

################################################################################
# SETUP LOGGING
################################################################################

pathToThisPyFile = inspect.getfile(inspect.currentframe())
path, filename = os.path.split(pathToThisPyFile)
filename = os.path.splitext(filename)[0] + '.log'
log_folder_path = os.path.join(path, 'logs')
if not os.path.exists(log_folder_path):
    os.mkdir(log_folder_path)
log_path = os.path.join(log_folder_path, filename)

# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - [%(levelname)s] %(name)s [%(module)s, line %(lineno)d]: %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=log_path,
                    filemode='w')

# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(name)s [%(module)s, line %(lineno)d]: %(message)s')

# define handlers
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)

file_log = TimedRotatingFileHandler(log_path, when='W6')
file_log.setLevel(logging.DEBUG)
console.setFormatter(formatter)

# add the handlers to the root logger
logging.getLogger('').addHandler(console)
logging.getLogger('').addHandler(file_log)

log = logging.getLogger(__name__)

def main(args, dummy_run):

    print '----------------------------------------------------------------'
    print 'starting up exiftool'

    et.start()

    for arg in args:
        process(arg, dummy_run)

    print 'closing exiftool'

    et.terminate()

    print '----------------------------------------------------------------'


def process(root_path, dummy_run):
    print 'starting to process (%s)' % root_path

    if not os.path.isdir(root_path):
        print 'ERROR path is not a folder (%s)' % root_path
        return False

    for dirName, subdirList, fileList in os.walk(root_path):
        for f in fileList:
            file_path = os.path.join(dirName, f)
            if not utils_fs.isfile(file_path, settings.MEDIA_FILE_EXTENSIONS):
                continue
            print 'file: %s' % file_path
            file_exif = et.get_metadata(file_path)
            _, oldest_date, oldest_date_tag = sortphotos.get_oldest_timestamp(file_exif, ['File'], [])
            print oldest_date_tag
            if oldest_date is not None:
                oldest_time = time.mktime(oldest_date.timetuple())
                print "oldest date: %s (tag: %s)" % (oldest_date, oldest_date_tag)
                print "writing to file's create date..."
                if not dummy_run:
                    os.utime(file_path, (oldest_time, oldest_time))


if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-d", "--dummy_run")

    (options, args) = parser.parse_args()

    main(args, dummy_run=options.dummy)

