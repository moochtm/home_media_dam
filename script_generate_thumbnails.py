
import os
import inspect
import sys
import settings

from src.api.core import utils_preview, utils_fs

pathToThisPyFile = inspect.getfile(inspect.currentframe())

################################################################################
# SETUP LOGGING
################################################################################

import logging

pathToThisPyFile = inspect.getfile(inspect.currentframe())
path, filename = os.path.split(pathToThisPyFile)
filename = os.path.splitext(filename)[0] + '.log'
log_path = os.path.join(path, filename)

# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - [%(levelname)s] %(name)s [%(module)s, line %(lineno)d]: %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=log_path,
                    filemode='w')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(name)s [%(module)s, line %(lineno)d]: %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

def run():

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
    for dirName, subdirList, fileList in os.walk(settings.HOMEMEDIA_ROOT):
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
            if utils_fs.isfile(fpath, settings.MEDIA_FILE_EXTENSIONS):
                for res in (settings.PREVIEW_MIN_RES, settings.PREVIEW_MAX_RES):
                    logger.info('asset: %s' % fpath)
                    utils_preview.get_binary_and_mime(full_path=fpath, longest_edge_res=res, no_return=True)

    # UNLOCK
    # ------------------------------------------
    os.remove('%s.locked' % pathToThisPyFile)


if __name__ == '__main__':
    sys.exit(run())