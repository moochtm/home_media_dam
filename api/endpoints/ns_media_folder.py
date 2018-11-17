
import logging
log = logging.getLogger(__name__)


from flask_restplus import Namespace, Resource, fields
from flask import request
import urlparse, urllib
import json

from api.core import utils_fs
import ns_media_file
import settings

api = Namespace('mediafolder', description='Browse folders')

#################################################################################


class MediaFolder():
    """
    Handles all MediaFolder response building.
    """
    def __init__(self, path, big_file_list=False):
        self.rel_path = path
        self.full_path = utils_fs.join_path(settings.HOMEMEDIA_ROOT, path)
        self._big_file_list = big_file_list

    def isdir(self):
        return utils_fs.isdir(self.full_path)

    @property
    def metadata(self):
        if not self.isdir():
            return None

        folder = {}
        folder['name'] = utils_fs.get_basename(self.full_path)
        folder['path'] = self.rel_path
        if self.rel_path != '':
            folder['parentPath'], _ = utils_fs.get_path_split(self.rel_path)
        folder['createdDate'] = utils_fs.get_creation_date(self.full_path)

        # if not just a big file list, get subfolders
        if not self._big_file_list:
            folder['subFolders'] = []
            sfs = utils_fs.get_folders(self.full_path, settings.FOLDER_PREFIX_BLACKLIST)
            for item in sfs:
                sf = {}
                sf['name'] = utils_fs.get_basename(item)
                sf['path'] = item[len(settings.HOMEMEDIA_ROOT)+1:]
                if sf['path'] != '':
                    sf['parentPath'], _ = utils_fs.get_path_split(sf['path'])
                sf['createdDate'] = utils_fs.get_creation_date(item)
                folder['subFolders'].append(sf)

            # sort subfolders by name
            folder['subFolders'] = sorted(folder['subFolders'], key=lambda i: (i['name'].lower()))

        # get media files
        folder['mediaFiles'] = []

        include_subfolders = False
        if self._big_file_list:
            include_subfolders = True

        mfs_paths = utils_fs.get_files(self.full_path, extensions=settings.MEDIA_FILE_EXTENSIONS,
                                       folder_prefix_blacklist=settings.FOLDER_PREFIX_BLACKLIST,
                                       include_subfolders=include_subfolders)
        log.debug('mfs: %s' % mfs_paths)

        if len(mfs_paths) > 0:
            mfs = ns_media_file.MediaFiles(mfs_paths)
            mfs.get_exif_for_all_files()

            for mf in mfs._files:
                metadata = mf.read_metadata()
                # log.debug('mf.read_metadata(): %s' % metadata)
                folder['mediaFiles'].append(metadata)

        # sort the media files by created date
        # TODO: part of fetching EXIF
        folder['mediaFiles'] = sorted(folder['mediaFiles'], key=lambda i: (i['createdDate']), reverse=True)

        """
        for mfp in mfs:
            mf = ns_media_file.MediaFile(mfp)
            if mf.is_mediafile:
                metadata = mf.read_metadata()
                # log.debug('mf.read_metadata(): %s' % metadata)
                folder['mediaFiles'].append(metadata)
        """

        # log.debug(json.dumps(folder, sort_keys=True, indent=4))
        return folder

#################################################################################


class URL(fields.Raw):
    def format(self, value):
        split_url = urlparse.urlsplit(request.url)
        return urlparse.urlunsplit(
                (split_url.scheme, split_url.netloc, '/' + api.name + '/' + urllib.quote(value), '', '')
        )


folder_model = api.model('folder_model', {
    'name': fields.String(description='Folder name'),
    # TODO: remove path if not needed
    #'path': fields.String(description='Folder path'),
    'parentUrl': URL(attribute='parentPath'),
    'url': URL(attribute='path'),
})


media_folder_model = api.clone('media_folder_model', folder_model,
                             {
                                'subFolders': fields.List(fields.Nested(folder_model), required=True),
                                'mediaFiles': fields.List(fields.Nested(ns_media_file.media_file_model), required=True)
                             })

#################################################################################


@api.route('/')
@api.route('/<path:path>')
class MediaFolderAPI(Resource):
    """
    Handles all MediaFolder REST methods
    """

    @api.marshal_with(media_folder_model)
    @api.response(404, 'Path not Found')
    @api.response(400, 'Bad Request')
    @api.response(200, 'All good')
    def get(self, path=''):
        """
        Returns details of the folder, and that of any subfolders and media files it contains.
        param {path}: the path to the folder (optional)
        :return: Details of the folder, and that of any subfolders and media files it contains.
        """
        # Check payload: there shouldn't be any. Return 400 if there is.
        if api.payload is not None:
            return 400, "Bad Request: Should not be a payload"

        params = dict(urlparse.parse_qsl(urlparse.urlsplit(request.url).query))
        log.debug('parameters: %s' % params)

        big_file_list = False
        if 'big_file_list' in params and params['big_file_list'] == 'true':
            big_file_list = True

        log.debug('path: %s' % path)
        f = MediaFolder(path, big_file_list)
        # if not a valid path, MediaFolder() = False
        if not f.isdir():
            return 404, "Path not Found: %s" % f.full_path


        # log.debug(f.metadata)

        # return
        return f.metadata

##################################################################
# tests
##################################################################

if __name__ == "__main__":
     f = MediaFolder('')
     print f.metadata