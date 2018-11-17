
import utils_fs
import utils_cache
import utils_images

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

        if response == True and not no_return:
            # (try to) get pre-cached file, as long as we're not cache-busting
            response = utils_cache.get_file_binary(cache_filename)

    if not response:

        # if there was no pre-cached file...
        log.debug('File not found in cache (%s)' % cache_filename)

        # get a generated binary and mime to return
        response = utils_images.get_jpeg_binary(full_path, longest_edge_res)

        # cache the generated binary for next time
        utils_cache.store_binary_file(cache_filename, response, str(year))

    # the mime will always be jpeg for preview images
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

##################################################################
# tests
##################################################################


def main():
    import settings

    full_path = '/Users/home/Pictures/test.CR2'
    longest_edge_res = settings.PREVIEW_MIN_RES

    print get_binary_and_mime(full_path, longest_edge_res)

    # print get_metadata_batch(['/Users/Home/Pictures/test.cr2'])


if __name__ == "__main__":
    main()
