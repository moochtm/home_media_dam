from flask_restplus import Namespace, Resource, inputs

from src.api.core import utils_fs
import src.api.data_models as data_models
import settings

import logging
log = logging.getLogger(__name__)

api = Namespace('browse', description='browse folders')

# https://helpcenter.woodwing.com/hc/en-us/articles/115002690126-Elvis-6-REST-API-browse

#################################################################################

parser = api.parser()
parser.add_argument('path', type=str, help='path to the folder you want to list', default='')
parser.add_argument('include_folders', type=inputs.boolean, help='indicates if sub-folders should be returned', default=True)
parser.add_argument('full_tree', type=inputs.boolean, help='should tree of all folders be returned', default=False)
parser.add_argument('include_assets', type=inputs.boolean, help='indicates if assets should be returned', default=True)
parser.add_argument('flatten_folders', type=inputs.boolean, help='indicates if assets from sub-folders '
                                                      'should be returned as one long list', default=False)
parser.add_argument('include_assets', type=inputs.boolean, help='indicates if assets should be returned', default=True)

#################################################################################
# BROWSE Class
#################################################################################


@api.route('')
class Browse(Resource):

    #################################################################################
    # GET browse
    #################################################################################

    @api.expect(parser, validate=True)
    @api.marshal_with(data_models.recursive_folder_model())
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

        # Check vars
        if not utils_fs.isdir(full_path):
            return "Bad Path: Path is not a folder", 404

        # Start browsing
        response = dict()
        response['path'] = args['path']

        # Get sub-folders
        if args['include_folders']:
            self._populate_children(parent=response, full_tree=args['full_tree'])
        print response

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

    #################################################################################
    # Utility functions
    #################################################################################

    def _populate_children(self, parent, full_tree=False):
        full_path = utils_fs.join_path(settings.HOMEMEDIA_ROOT, parent['path'])
        children = utils_fs.get_folders(full_path,
                                        settings.FOLDER_PREFIX_BLACKLIST,
                                        include_subfolders=False)
        print len(children)
        if len(children) > 0:
            parent['children'] = []
            for folder in children:
                folder = folder[len(settings.HOMEMEDIA_ROOT) + 1:]
                child = {'path': folder}
                if full_tree:
                    self._populate_children(parent=child, full_tree=full_tree)
                parent['children'].append(child)

            # sort sub-folders by name
            parent['children'] = sorted(parent['children'], key=lambda i: (i['path'].lower()))
            # Note that additional metadata is added to folders automatically using restplus marshalling

        return parent
