import logging
log = logging.getLogger(__name__)


from flask_restplus import Namespace, Resource, inputs
from flask import request
import urlparse

from ..core import utils_fs
from ..data_models import folder_model
import settings

api = Namespace('browse', description='browse folders')

# https://helpcenter.woodwing.com/hc/en-us/articles/115002690126-Elvis-6-REST-API-browse

#################################################################################

parser = api.parser()
parser.add_argument('path', type=str, help='path to the folder you want to list', default='')
parser.add_argument('include_folders', type=inputs.boolean, help='indicates if sub-folders should be returned', default=True)
parser.add_argument('include_assets', type=inputs.boolean, help='indicates if assets should be returned', default=True)
parser.add_argument('flatten_folders', type=inputs.boolean, help='indicates if assets from sub-folders '
                                                      'should be returned as one long list', default=False)

#################################################################################
# BROWSE Class
#################################################################################


@api.route('')
class Browse(Resource):

    #################################################################################
    # GET browse
    #################################################################################

    @api.expect(parser, validate=True)
    @api.marshal_with(folder_model)
    @api.response(404, 'Bad Path')
    @api.response(400, 'Bad Request')
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    def get(self):

        # Get parameters
        args = parser.parse_args()
        log.debug(args)

        # Check parameters
        print args['include_folders']
        print args['flatten_folders']
        #if args['includeFolders'] and args['flattenFolders']:
        #    return "includeFolders and flattenFolders cannot both be True", 400

        # Build vars
        full_path = utils_fs.join_path(settings.HOMEMEDIA_ROOT, args['path'])

        # Check vars
        if not utils_fs.isdir(full_path):
            return "Bad Path: Path is not a folder", 404

        # Start browsing
        response = {}
        response['path'] = args['path']

        # Get sub-folders
        if args['include_folders']:
            response['children'] = []
            subfolders = utils_fs.get_folders(full_path,
                                              settings.FOLDER_PREFIX_BLACKLIST,
                                              include_subfolders=args['flatten_folders'])
            for folder in subfolders:
                folder = folder[len(settings.HOMEMEDIA_ROOT) + 1:]
                response['children'].append({'path': folder})
            # sort subfolders by name
            response['children'] = sorted(response['children'], key=lambda i: (i['path'].lower()))
            # Note that additional metadata is added to folders automatically using restplus marshalling

        # Get assets
        if args['include_assets']:
            response['assets'] = []
            assets = utils_fs.get_files(full_path,
                                        extensions=settings.MEDIA_FILE_EXTENSIONS,
                                        folder_prefix_blacklist=settings.FOLDER_PREFIX_BLACKLIST,
                                        include_subfolders=args['flatten_folders'])
            for asset in assets:
                asset = asset[len(settings.HOMEMEDIA_ROOT) + 1:]
                response['assets'].append({'path': asset})
                # Note that additional metadata is added to assets automatically using restplus marshalling

        return response