import logging

log = logging.getLogger(__name__)

from flask_restplus import Api

import settings

api = Api(
    title='Home Media API',
    version='1.0',
    description='A REST API for managing media files on a NAS',
    # All API metadatas
)


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(e)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500
