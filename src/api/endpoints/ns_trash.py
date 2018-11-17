import logging
log = logging.getLogger(__name__)


from flask_restplus import Namespace, Resource, inputs
from flask import request
import urlparse

from ..core import utils_fs
import settings

api = Namespace('trash', description='trash files')

# https://helpcenter.woodwing.com/hc/en-us/articles/115002663483-Elvis-6-REST-API-remove

#################################################################################
#################################################################################
#################################################################################

parser = api.parser()
parser.add_argument('path', required=True, type=str, help='path of asset to trash')
parser.add_argument('restore', type=inputs.boolean, help='if true, attempts to restore the given path from trash')

#################################################################################
# TRASH Class
#################################################################################


@api.route('')
class Trash(Resource):

    #################################################################################
    # PUT trash
    #################################################################################

    @api.expect(parser, validate=True)
    @api.response(404, 'Bad Path')
    @api.response(405, 'The method is not allowed for the requested URL.')
    @api.response(400, 'Bad Request')
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    def put(self):

        # Check parameters
        args = parser.parse_args()
        log.debug(args)

        # Build full paths
        src_path = utils_fs.join_path(settings.HOMEMEDIA_ROOT, args['path'])
        trash_path = settings.IMAGE_TRASH_PATH

        # Check paths
        if not utils_fs.isdir(trash_path):
            return "Bad Path: Trash path is not a folder", 404

        # Try the trash
        if args['restore']:
            successful = utils_fs.restore(src_path=src_path, trash_path=trash_path)
        else:
            successful = utils_fs.trash(src_path=src_path, trash_path=trash_path)

        # TODO - create a response containing the necessary info to undo

        if successful:
            return "Success", 200
        return "Internal Server Error", 500