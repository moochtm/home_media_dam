import os
import inspect
import sys
import settings

import logging
from logging.handlers import TimedRotatingFileHandler

from src.api.core import utils_redis, utils_fs

pathToThisPyFile = inspect.getfile(inspect.currentframe())

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

format_string = '%(asctime)s - [%(levelname)s] %(name)s [%(module)s, line %(lineno)d]: %(message)s'

# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format=format_string,
                    datefmt='%Y-%m-%d %H:%M')

# set a format which is simpler for console use
formatter = logging.Formatter(format_string)

# define handler
file_log = TimedRotatingFileHandler(log_path, when='W6')
file_log.setLevel(logging.DEBUG)
file_log.setFormatter(formatter)

# add the handlers to the root logger
logging.getLogger().addHandler(file_log)

logger = logging.getLogger(__name__)

################################################################################
# MAIN
################################################################################

def run(root_folder=settings.HOMEMEDIA_ROOT, media_file_extensions=settings.MEDIA_FILE_EXTENSIONS):
    logger.info('Starting...')
    pathToThisPyFile = inspect.getfile(inspect.currentframe())

    # LOCK
    # ------------------------------------------
    locked = os.path.exists('%s.locked' % pathToThisPyFile)
    if locked:
        logger.warning('Script is locked. Exiting')
        sys.exit()
    else:
        open('%s.locked' % pathToThisPyFile, 'a').close()

    # DO THE WORK
    # ------------------------------------------
    for dirName, subdirList, fileList in os.walk(root_folder):
        tempdirs = []
        for dir in subdirList:
            blacklisted = False
            for prefix in settings.FOLDER_PREFIX_BLACKLIST:
                if dir.startswith(prefix):
                    logger.info('Blacklisted folder: %s' % os.path.join(dirName, dir))
                    blacklisted = True
            if not blacklisted:
                logger.info('Okayed folder: %s' % os.path.join(dirName, dir))
                tempdirs.append(dir)
        subdirList[:] = tempdirs

        for fname in fileList:
            fpath = os.path.join(dirName, fname)
            if utils_fs.isfile(fpath, media_file_extensions):
                logger.info('asset: %s' % fpath)
                utils_redis.add_preview_task_to_redis(full_path=fpath)

    # UNLOCK
    # ------------------------------------------
    os.remove('%s.locked' % pathToThisPyFile)


if __name__ == '__main__':
    root_folder = ''
    media_file_extensions = ['.HEIC']

    sys.exit(run(media_file_extensions=media_file_extensions))
    # sys.exit(run())
