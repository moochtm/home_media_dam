
import utils_fs
import utils_cache
import utils_images
import settings

import logging
log = logging.getLogger(__name__)


def get_binary_and_mime(full_path, longest_edge_res, cache_bust=False, no_return=False):
    # get binary and mime for sending.
    # if no pre-cached image, get a generated one and cache it.

    # get constructed cache filename
    cache_filename = get_cache_filename(full_path, longest_edge_res)

    # get year from file createdDate
    year = utils_fs.get_creation_year(full_path)

    response = False
    if not cache_bust:

        response = utils_cache.check_file_exists(filename=cache_filename, year=year)

        if response and not no_return:
            # (try to) get pre-cached file, as long as we're not cache-busting
            response = utils_cache.get_file_binary(cache_filename)

    if not response:

        # if there was no pre-cached file...
        log.info('File not found in cache (%s)' % cache_filename)

        # get a generated binary and mime to return
        response = utils_images.get_jpeg_binary(full_path, longest_edge_res)

        # cache the generated binary for next time
        utils_cache.store_binary_file(cache_filename, response, str(year))

    # the mime will always be jpeg for previews images
    mime = "image/jpeg"

    return response, mime


def get_cache_filename(full_path, longest_edge_res):
    # generate cache file name: orig filename-creation date-parameters

    cache_name = '%s_%s_%s.jpg' % (
        utils_fs.get_basename(full_path),
        utils_fs.get_creation_date(full_path).replace(':', '-'),
        str(longest_edge_res) + 'px')

    cache_name = cache_name.replace(':', '-')
    cache_name = cache_name.replace(' ', '-')

    return cache_name


def cache_all_preview_images(full_path, cache_bust=False):
    for res in [settings.PREVIEW_MIN_RES, settings.PREVIEW_MAX_RES]:
        cache_preview_image(full_path, longest_edge_res=res, cache_bust=cache_bust)


def cache_preview_image(full_path, longest_edge_res, cache_bust=False):
    # get constructed cache filename
    cache_filename = get_cache_filename(full_path, longest_edge_res)

    # get year from file createdDate
    year = utils_fs.get_creation_year(full_path)

    preview_image_exists = False
    if not cache_bust:
        preview_image_exists = utils_cache.check_file_exists(filename=cache_filename, year=year)

    if not preview_image_exists:
        # if there was no pre-cached file...
        log.info('Generating preview (%s)' % cache_filename)

        # get a generated binary
        binary = utils_images.get_jpeg_binary(full_path, longest_edge_res)

        # cache the generated binary for next time
        utils_cache.store_binary_file(cache_filename, binary, str(year))

        # check again if preview image exists (it really should!)
        preview_image_exists = utils_cache.check_file_exists(filename=cache_filename, year=year)

    else:
        log.info('Preview found in cache (%s)' % cache_filename)

    return preview_image_exists


##################################################################
# tests
##################################################################


def main():

    full_path = '/Users/home/Pictures/test.CR2'

    cache_all_preview_images(full_path)


if __name__ == "__main__":
    main()
