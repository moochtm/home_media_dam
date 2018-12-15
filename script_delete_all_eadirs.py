import os
import inspect
import subprocess
import sys

import settings

import logging
from logging.handlers import TimedRotatingFileHandler

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

def run(root_path, search_term):
    logger.info('starting...')
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

    find_and_delete_cmd = 'find "' + root_path +'" -name "' + search_term + '" -type d -exec rm -r "{}" +'
    find_cmd = 'find "' + root_path + '" -name "' + search_term + '" -type d'

    logger.debug("find cmd: %s" % find_cmd)
    try:
        result = filter(None, subprocess.check_output(find_cmd, shell=True).split('\n'))
    except subprocess.CalledProcessError as e:
        logger.error(e.output)
    logger.info('listing find results...')
    for item in result:
        logger.info(item)

    logger.debug("find and delete cmd: %s" % find_and_delete_cmd)
    try:
        subprocess.check_output(find_and_delete_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(e.output)

    # UNLOCK
    # ------------------------------------------
    os.remove('%s.locked' % pathToThisPyFile)

    logger.info('...finished')

if __name__ == '__main__':
    root_path = settings.HOMEMEDIA_ROOT
    search_term = '@eaDir'
    sys.exit(run(root_path=root_path, search_term=search_term))
