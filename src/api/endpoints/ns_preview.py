import logging
log = logging.getLogger(__name__)


from flask_restplus import Namespace, Resource, inputs
from flask import request, send_file
import urlparse

from ..core import utils_preview, utils_fs
from ..data_models import folder_model
import settings

api = Namespace('preview', description='get preview image for asset')

# https://helpcenter.woodwing.com/hc/en-us/articles/115002690126-Elvis-6-REST-API-browse

#################################################################################

parser = api.parser()
parser.add_argument('path', type=str, help='path to the folder you want to list', required=True)
parser.add_argument('max_quality', type=inputs.boolean, help='return the max quality level preview', default=False)
parser.add_argument('cache_bust', type=str, help='force regen of the cached image', default='False')

#################################################################################
# PREVIEW Class
#################################################################################


@api.route('')
class Preview(Resource):

    #################################################################################
    # GET preview
    #################################################################################

    @api.expect(parser, validate=True)
    @api.response(404, 'Bad Path')
    @api.response(400, 'Bad Request')
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    def get(self):

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

        # Start response
        # response =

        binary, mime = utils_preview.get_binary_and_mime(full_path, longest_edge_res, cache_bust)

        # seek back to 0 just in case!
        binary.seek(0)

        return send_file(binary, mimetype=mime)