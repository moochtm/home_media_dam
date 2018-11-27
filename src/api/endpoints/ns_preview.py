
import os
from flask_restplus import Namespace, Resource, inputs
from flask import request, send_file, send_from_directory
import urlparse

from src.api.core import utils_preview
from src.api.core import utils_fs
import settings

import logging
log = logging.getLogger(__name__)

api = Namespace('previews', description='get previews image for asset')

# https://helpcenter.woodwing.com/hc/en-us/articles/115002690126-Elvis-6-REST-API-browse

#################################################################################

parser = api.parser()
parser.add_argument('path', type=str, help='path to the folder you want to list', required=True)
parser.add_argument('max_quality', type=inputs.boolean, help='return the max quality level previews', default=False)
parser.add_argument('cache_bust', type=str, help='force regen of the cached image', default='False')
parser.add_argument('send_binary', type=str, default='False')

#################################################################################
# PREVIEW Class
#################################################################################


@api.route('')
@api.route('/<path:cache_path>')
class Preview(Resource):

    #################################################################################
    # GET previews
    #################################################################################

    @api.expect(parser, validate=True)
    @api.response(404, 'Bad Path')
    @api.response(400, 'Bad Request')
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    def get(self, cache_path):

        print cache_path
        cache_fullpath = os.path.join(settings.IMAGE_CACHE_PATH, cache_path)
        if os.path.isfile(cache_fullpath):
            directory, filename = os.path.split(cache_fullpath)
            return send_from_directory(directory=directory, filename=filename)

        # Get parameters
        args = parser.parse_args()
        log.debug(args)

        # Build vars
        full_path = utils_fs.join_path(settings.HOMEMEDIA_ROOT, args['path'])
        cache_bust = False
        if args['cache_bust'] != 'False':
            cache_bust = True

        longest_edge_res = settings.PREVIEW_MIN_RES
        if args['max_quality']:
            longest_edge_res = settings.PREVIEW_MAX_RES

        # Check vars
        if not utils_fs.isfile(full_path, settings.MEDIA_FILE_EXTENSIONS):
            log.error("Bad Path: Path is not a supported file (%s)" % full_path)
            return "Bad Path: Path is not a supported file", 404

        if args['send_binary']:
            binary, mime = utils_preview.get_binary_and_mime(full_path, longest_edge_res, cache_bust)
            binary.seek(0)
            send_file(binary)
        else:
            directory, filename = utils_preview.get_cache_fullpath(full_path, longest_edge_res, cache_bust)
            send_from_directory(directory=directory, filename=filename)