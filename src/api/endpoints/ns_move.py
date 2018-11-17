from flask_restplus import Namespace, Resource, fields, reqparse

from src.api.core import utils_fs
import settings

import logging
log = logging.getLogger(__name__)

api = Namespace('move', description='move files')

# https://helpcenter.woodwing.com/hc/en-us/articles/115002690306-Elvis-6-REST-API-move-rename

#################################################################################
#################################################################################
#################################################################################

parser = api.parser()
parser.add_argument('src_path', required=True, type=str, help='source path')
parser.add_argument('dest_path', required=True, type=str, help='destination path')

#################################################################################
# MOVE Class
#################################################################################


@api.route('')
class Move(Resource):

    #################################################################################
    # PUT move
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
        source_path = utils_fs.join_path(settings.HOMEMEDIA_ROOT, args['src_path'])
        target_path = utils_fs.join_path(settings.HOMEMEDIA_ROOT, args['dest_path'])

        # Check paths
        if not utils_fs.isfile(source_path):
            return "Bad Path: Source path is not a file", 404
        if not utils_fs.isdir(target_path):
            return "Bad Path: Target path is not a folder", 404

        # Try the move
        successful = utils_fs.move(src_path=source_path, dest_path=target_path)

        if successful:
            return "Success", 200
        return "Internal Server Error", 500