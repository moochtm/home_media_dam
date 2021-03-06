from flask_restplus import Namespace, Resource, inputs

from src.api.data_models import init_model
import settings

import logging
log = logging.getLogger(__name__)

api = Namespace('init', description='pass init variables to web')

# https://helpcenter.woodwing.com/hc/en-us/articles/115002663483-Elvis-6-REST-API-remove

#################################################################################

#################################################################################
# INIT Class
#################################################################################


@api.route('')
class Init(Resource):

    #################################################################################
    # GET init
    #################################################################################

    @api.marshal_with(init_model)
    @api.response(400, 'Bad Request')
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    def get(self):

        response = dict()
        response['inbox_folder_path'] = settings.HOMEMEDIA_INBOX
        response['archive_folder_path'] = settings.HOMEMEDIA_ARCHIVE

        # URLs
        # - browse
        # "code_search_url": "https://api.github.com/search/code?q={query}{&page,per_page,sort,order}"
        # '/browse?path={path}'
        # - trash
        # - un-trash
        # - move
        # - smallPreview
        # - largePreview
        # - generatePreviews

        # configured paths
        # - inbox
        # - archive

        return response
