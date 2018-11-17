
import os
import inspect
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask
from flask_cors import CORS

from api.endpoints.ns_move import api as ns5
from api.endpoints.ns_browse import api as ns6
from api.endpoints.ns_trash import api as ns7
from api.endpoints.ns_preview import api as ns8
from api.endpoints.ns_init import api as ns9

from api.restplus import api
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

################################################################################
# SETUP FLASK
################################################################################

app = Flask(__name__)


def configure_app(flask_app):
    # flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    CORS(app)
    configure_app(flask_app)

    api.add_namespace(ns5)
    api.add_namespace(ns6)
    api.add_namespace(ns7)
    api.add_namespace(ns8)
    api.add_namespace(ns9)


def main():
    log.info("================================================================")
    log.info("================================================================")
    log.info("================================================================")
    log.info("Initialising app")
    initialize_app(app)
    api.init_app(app)
    app.run(debug=settings.API_FLASK_DEBUG, host=settings.API_FLASK_SERVER_HOST, port=settings.API_FLASK_SERVER_PORT)


if __name__ == "__main__":
    main()

    # TODO: check all important settings exist and have valid values


