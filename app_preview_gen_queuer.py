
import os
import inspect
import logging
from logging.handlers import TimedRotatingFileHandler

import time, sys
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from src.api.core import utils_redis
import settings

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

log = logging.getLogger(__name__)


################################################################################
# STUFF
################################################################################

log.info("================================================================")
log.info("Initialising app")


class MyHandler(PatternMatchingEventHandler):
    patterns = ['*' + ext for ext in settings.MEDIA_FILE_EXTENSIONS]
    log.info("Watch patterns: %s" % patterns)

    def on_created(self, event):
        log.info("File created: %s" % event.src_path)
        utils_redis.add_preview_task_to_redis(event.src_path)

    def on_modified(self, event):
        log.info("File modified: %s" % event.src_path)


if __name__ == '__main__':

    log.info("Watch path: %s" % settings.HOMEMEDIA_ROOT)

    observer = Observer()
    observer.schedule(MyHandler(), path=settings.HOMEMEDIA_ROOT, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
