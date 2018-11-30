from flask_restplus import fields

from core import utils_fs
from core import utils_preview
from restplus import api
import settings

from flask import request

import urlparse, urllib


class BrowseUrl(fields.Raw):
    def format(self, value):
        split_url = urlparse.urlsplit(request.url)
        path = "/browse"
        query = "path=%s" % urllib.quote(value)
        return urlparse.urlunsplit((split_url.scheme, split_url.netloc, path, query, ''))


class Children(fields.Raw):
    def format(self, value):
        full_path = utils_fs.join_path(settings.HOMEMEDIA_ROOT, value)
        if len(utils_fs.get_folders(full_path, prefix_blacklist=settings.FOLDER_PREFIX_BLACKLIST)) > 0:
            return []
        else:
            return False


class LightboxUrl(fields.Raw):
    def format(self, value):
        split_url = urlparse.urlsplit(request.url)
        path = '/previews'
        query = 'path=%s&max_quality=true' % value
        return urlparse.urlunsplit((split_url.scheme, split_url.netloc, path, query, ''))


class MoveUrl(fields.Raw):
    def format(self, value):
        split_url = urlparse.urlsplit(request.url)
        path = '/move'
        query = ''
        return urlparse.urlunsplit((split_url.scheme, split_url.netloc, path, query, ''))


class ThumbnailUrl(fields.Raw):
    def format(self, value):
        split_url = urlparse.urlsplit(request.url)
        path = '/previews'
        query = 'path=%s' % value
        return urlparse.urlunsplit((split_url.scheme, split_url.netloc, path, query, ''))


class TrashUrl(fields.Raw):
    def format(self, value):
        split_url = urlparse.urlsplit(request.url)
        path = '/trash'
        query = 'path=%s' % urllib.quote(value)
        return urlparse.urlunsplit((split_url.scheme, split_url.netloc, path, query, ''))


class CreatedDate(fields.Raw):
    def format(self, value):
        full_path = utils_fs.join_path(settings.HOMEMEDIA_ROOT, value)
        return utils_fs.get_creation_date(full_path)


class Name(fields.Raw):
    def format(self, path):
        return utils_fs.get_basename(path)


class ParentBrowseUrl(fields.Raw):
    def format(self, value):
        if value == '':
            return None
        value, _ = utils_fs.get_path_split(value)

        split_url = urlparse.urlsplit(request.url)
        path = "/browse"
        query = "path=%s" % urllib.quote(value)
        return urlparse.urlunsplit((split_url.scheme, split_url.netloc, path, query, ''))


class ParentPath(fields.Raw):
    def format(self, value):
        if value == '':
            return None
        value, _ = utils_fs.get_path_split(value)
        return value


init_model = api.model('init_model', {
    'inbox_folder_path': fields.String(),
    'archive_folder_path': fields.String()
})


base_folder_model = api.model('base_folder_model', {
    'path': fields.String(),
    'name': Name(attribute='path'),
    'children': Children(attribute='path'),
    'browseUrl': BrowseUrl(attribute='path'),
    'createdDate': CreatedDate(attribute='path'),
    'parentBrowseUrl': ParentBrowseUrl(attribute='path')
})

base_asset_model = api.model('base_asset_model', {
    'path': fields.String(),
    'name': Name(attribute='path'),
    'createdDate': CreatedDate(attribute='path'),
    'moveUrl': MoveUrl(attribute='path'),
    'thumbnailUrl': ThumbnailUrl(attribute='path'),
    'parentBrowseUrl': ParentBrowseUrl(attribute='path'),
    'parentPath': ParentPath(attribute='path'),
    'lightboxUrl': LightboxUrl(attribute='path'),
    'trashUrl': TrashUrl(attribute='path'),
})

folder_model = api.clone('folder_model', base_folder_model,
                         {
                             'children': fields.List(fields.Nested(base_folder_model)),
                             'assets': fields.List(fields.Nested(base_asset_model))
                         })
