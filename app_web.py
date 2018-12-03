import inspect
import logging
from logging.handlers import TimedRotatingFileHandler

import os
import urlparse

from flask import Flask, render_template

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
# SETUP FLASK
################################################################################


my_path, _ = os.path.split(os.path.realpath(__file__))
static_path = os.path.join(my_path, 'src/web/static')
templates_path = os.path.join(my_path, 'src/web/templates')
print static_path


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='(%',
        block_end_string='%)',
        variable_start_string='((',
        variable_end_string='))',
        comment_start_string='(#',
        comment_end_string='#)',
    ))


app = CustomFlask(__name__, static_folder=static_path, template_folder=templates_path)

scheme = 'http'
netloc = '%s:%s' % (settings.API_FLASK_SERVER_HOST, settings.API_FLASK_SERVER_PORT)
path = settings.API_INITIAL_RESOURCE
query = settings.API_INITIAL_QUERY
api_endpoint_url = urlparse.urlunsplit((scheme, netloc, path, query, ''))

print api_endpoint_url


@app.route('/')
def root():
    return render_template('index.html', jinja_var_api_endpoint=api_endpoint_url)


if __name__ == "__main__":

    log.info("================================================================")
    log.info("INITIALISING APP")
    log.info("================================================================")

    app.run(host=settings.API_FLASK_SERVER_HOST, port=6502)
