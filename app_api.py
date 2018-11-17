
import os
import logging.config
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), './logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)

from flask import Flask
from flask_cors import CORS

from api.endpoints.ns_media_folder import api as ns3
from api.endpoints.ns_media_file import api as ns4
from api.endpoints.ns_move import api as ns5
from api.endpoints.ns_browse import api as ns6
from api.endpoints.ns_trash import api as ns7
from api.endpoints.ns_preview import api as ns8
from api.endpoints.ns_init import api as ns9

from api.restplus import api
import settings

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
    api.add_namespace(ns3)
    api.add_namespace(ns4)
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


