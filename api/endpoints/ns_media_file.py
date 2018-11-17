
import logging
log = logging.getLogger(__name__)


from flask_restplus import Namespace, Resource, fields
from flask import send_file, request
import urlparse, urllib
import json

from api.core import utils_fs, utils_dict, utils_images, utils_exif
import ns_media_folder
import settings

api = Namespace('mediafile', description='Browse folders')

# TODO: editable exif keys needs to be based on the type of media file, should be determined by the MediaFile class
editable_exif_keys = [
    'EXIF:Rating'
]

#################################################################################
#################################################################################
#################################################################################


class MediaFile:
    """
    Handles all MediaFile response building.
    """
    def __init__(self, path):
        if settings.HOMEMEDIA_ROOT in path:
            path = path[len(settings.HOMEMEDIA_ROOT)+1:]
        self.rel_path = path
        log.debug('New MediaFile, path: %s' % path)

        self._metadata = None

    @property
    def full_path(self):
        return utils_fs.join_path(settings.HOMEMEDIA_ROOT, self.rel_path)

    @property
    def extension(self):
        return utils_fs.get_file_extension(self.full_path).upper()

    @property
    def is_mediafile(self):
        return utils_fs.isfile(self.full_path, settings.MEDIA_FILE_EXTENSIONS)

    @property
    def editable_exif_keys(self):
        """
        Returns dict of exiftool EXIF keys that can be edited, based on the file's extension
        :return: dict
        """
        ext = self.extension
        # TODO - push editable extensions into the settings file
        if ext == '.CR2':
            return ['EXIF:Rating']
        elif ext == '.JPG':
            return ['EXIF:Rating']
        else:
            return []

    def read_metadata(self):
        if not self.is_mediafile:
            return None

        file = {}
        file['name'] = utils_fs.get_basename(self.full_path)
        file['path'] = self.rel_path
        if self.rel_path != '':
            file['parentPath'], _ = utils_fs.get_path_split(self.rel_path)
        file['createdDate'] = utils_fs.get_creation_date(self.full_path)
        # TODO: delay fetching EXIF
        # file['editableExif'] = self.editable_exif_keys

        if self._metadata is None:
            pass
            # TODO: delay fetching EXIF
            # self._metadata = utils_exif.get_metadata_batch([self.full_path])[0]
        file['exif'] = self._metadata

        return file

    def write_metadata(self, metadata):
        """
        Sets select properties/metadata of the MediaFile.
        :param metadata: a dict matching the same format as the metadata getter.
        :return: True/False
        """
        log.debug(metadata)
        metadata['path'] = self.full_path
        for key in metadata['exif'].keys():
            if key not in self.editable_exif_keys:
                metadata['exif'].pop(key, None)

        if "EXIF:Rating" in metadata['exif']:
            rating = metadata['exif']["EXIF:Rating"]
            rating = str(rating)
            rating_to_percent = {'0': '0', '1': '1', '2': '25', '3': '50', '4': '75', '5': '100'}

            metadata['exif']["EXIF:RatingPercent"] = rating_to_percent[rating]
            metadata['exif']["XMP:Rating"] = rating
            metadata['exif']["XMP:RatingPercent"] = rating_to_percent[rating]

        log.debug('scrubbed metadata: %s' % metadata)
        return utils_exif.write_metadata_batch([metadata])

    def get_content_binary_and_mime(self, params):
        im = utils_images.Image(self.full_path, params)
        #im.process(options=params)
        binary = im.binary
        mime = im.mimetype
        return binary, mime

    def trash_me(self):
        return utils_fs.trash(self.full_path, settings.IMAGE_TRASH_PATH, log_in_history=True)


class MediaFiles:
    """
    Handles all MediaFile response building.
    """
    def __init__(self, paths):
        log.debug('New MediaFiles, paths: %s' % paths)

        self._files = []

        for path in paths:
            mf = MediaFile(path)
            if mf.is_mediafile:
                self._files.append(mf)

    def get_exif_for_all_files(self):
        # get a list of all file paths
        paths = []
        for mf in self._files:
            paths.append(mf.full_path)

        # get the exif for all files in one go
        # TODO: Delay fetching EXIF
        exif_for_all_files = None # utils_exif.get_metadata_batch(paths)

        #for mf in self._files:
        #    full_path = mf.full_path
        #    exif = [exif for exif in exif_for_all_files if exif['SourceFile'] == full_path][0]
        #    mf._metadata = exif
            # print full_path, exif

#################################################################################
#################################################################################
#################################################################################

class contentUrl(fields.Raw):
    __schema_type__ = 'string'
    def format(self, value):
        log.debug('URL file path: %s' % value)
        split_url = urlparse.urlsplit(request.url)
        return urlparse.urlunsplit(
            (split_url.scheme, split_url.netloc, '/' + api.name + '/content/' + urllib.quote(value), '', '')
        )

class metadataUrl(fields.Raw):
    __schema_type__ = 'string'
    def format(self, value):
        log.debug('URL file path: %s' % value)
        split_url = urlparse.urlsplit(request.url)
        return urlparse.urlunsplit(
            (split_url.scheme, split_url.netloc, '/' + api.name + '/metadata/' + urllib.quote(value), '', '')
        )


media_file_exif_model = api.model('media_file_exif_model', {
    'EXIF:CreateDate': fields.String(default="0000:00:00 00:00:00"),
    'EXIF:ModifyDate': fields.String(default="0000:00:00 00:00:00"),
    'EXIF:Rating': fields.Integer(default=0),
    'EXIF:Model': fields.String(default="not present"),
    'EXIF:Orientation': fields.String(default="not present")
})


media_file_model = api.model('media_file_model', {
    'name': fields.String(),
    'contentUrl': contentUrl(attribute='path'),
    'metadataUrl': metadataUrl(attribute='path'),
    'createdDate': fields.String(),
    'exif': fields.Nested(media_file_exif_model),
    'editableExif': fields.List(fields.String())
})

media_file_move_model = api.model('media_file_move_model', {
    'folderUrl': fields.String()
})


#################################################################################
# MediaFileMetadata Class
#################################################################################

@api.route('/metadata/<path:path>')
class MediaFileMetadata(Resource):

    #################################################################################
    # GET mediafile/metadata/
    #################################################################################

    @api.marshal_with(media_file_model)
    @api.response(404, 'Path not Found')
    @api.response(400, 'Bad Request')
    @api.response(200, 'All good')
    def get(self, path=''):
        """

        param {path}:
        :return:
        """
        # Check payload: there shouldn't be any. Return 400 if there is.
        log.debug('api.payload: %s' % api.payload)
        if api.payload is not None:
            return 400, "Bad Request: Should not be a payload"

        # Check parameters
        params = dict(urlparse.parse_qsl(urlparse.urlsplit(request.url).query))
        log.debug('parameters: %s' % params)
        if params != {}:
            return 400, "Bad Request: Should not be any parameters"

        log.debug('path: %s' % path)
        f = MediaFile(path)
        # if not a valid path, MediaFolder() = False
        if not f.is_mediafile:
            return 404, "Path not Found: %s" % f.full_path

        return f.read_metadata

    #################################################################################
    # PUT mediafile/metadata/
    #################################################################################

    @api.expect(media_file_model)
    @api.response(404, 'Path not Found')
    @api.response(400, 'Bad Request')
    @api.response(200, 'All good')
    def put(self, path=''):
        """

        param {path}:
        :return:
        """
        # Check parameters
        params = dict(urlparse.parse_qsl(urlparse.urlsplit(request.url).query))
        log.debug('parameters: %s' % params)
        if params != {}:
            return 400, "Bad Request: Should not be any parameters"

        log.debug('path: %s' % path)
        f = MediaFile(path)
        # if not a valid path, MediaFolder() = False
        if not f.is_mediafile:
            return 404, "Path not Found: %s" % f.full_path

        for key in api.payload['exif'].keys():
            if key not in editable_exif_keys:
                api.payload['exif'].pop(key, None)
        log.debug('scrubbed payload: %s' % api.payload)

        return f.write_metadata(api.payload)
        #return utils_exif.write_metadata_batch([api.payload])


#################################################################################
# MediaFileContent Class
#################################################################################

@api.route('/content/<path:path>')
class MediaFileContent(Resource):

    #################################################################################
    # GET mediafile/content/
    #################################################################################

    @api.response(404, 'Path not Found')
    @api.response(400, 'Bad Request')
    @api.response(200, 'All good')
    def get(self, path=''):
        """

        param {path}:
        :return:
        """
        # Check payload: there shouldn't be any. Return 400 if there is.
        # log.debug('api.payload: %s' % api.payload)
        if api.payload is not None:
            return 400, "Bad Request: Should not be a payload"

        path = urlparse.urlparse(path).path
        log.debug('path: %s' % path)
        f = MediaFile(path)
        # if not a valid path, MediaFolder() = False
        if not f.is_mediafile:
            return 404, "Path not Found: %s" % f.full_path

        params = dict(urlparse.parse_qsl(urlparse.urlsplit(request.url).query))
        log.debug('parameters: %s' % params)
        binary, mime = f.get_content_binary_and_mime(params)

        return send_file(binary, mimetype=mime)

    #################################################################################
    # PUT mediafile/content/
    #################################################################################

    @api.expect(media_file_move_model)
    @api.response(404, 'Path not Found')
    @api.response(400, 'Bad Request')
    @api.response(200, 'All good')
    def put(self, path=''):
        """
        MOVES A FILE TO A NEW FOLDER
        param {path}:
        :return:
        """
        path = urlparse.urlparse(path).path
        log.debug('path: %s' % path)
        f = MediaFile(path)
        # if not a valid path, MediaFolder() = False
        if not f.is_mediafile:
            return 404, "Path not Found: %s" % f.full_path

        log.debug('payload: %s' % api.payload)

        return True

    #################################################################################
    # DELETE mediafile/content/
    #################################################################################

    @api.response(404, 'Path not Found')
    @api.response(400, 'Bad Request')
    @api.response(200, 'All good')
    def delete(self, path=''):
        """

        :param path:
        :return:
        """
        # Check parameters
        params = dict(urlparse.parse_qsl(urlparse.urlsplit(request.url).query))
        log.debug('parameters: %s' % params)
        if params != {}:
            return 400, "Bad Request: Should not be any parameters"

        # Check payload: there shouldn't be any. Return 400 if there is.
        log.debug('api.payload: %s' % api.payload)
        if api.payload is not None:
            return 400, "Bad Request: Should not be a payload"

        path = urlparse.urlparse(path).path
        log.debug('path: %s' % path)
        f = MediaFile(path)
        # if not a valid path, MediaFolder() = False
        if not f.is_mediafile:
            return 404, "Path not Found: %s" % f.full_path

        return f.trash_me()

##################################################################
# tests
##################################################################


if __name__ == "__main__":
     f = MediaFile('test.cr2')
     f.write_metadata({u'url': u'http://192.168.1.112:6500/media/canon_7d2.2018-07-01.038A5058.CR2',
                  u'path': u'test.cr2', u'name': u'test.cr2', u'exif':{u'EXIF:Rating': 5}})
     print f.read_metadata()
