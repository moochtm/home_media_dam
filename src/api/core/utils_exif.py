
#######################################################################################
# Helper functions for working directly with media file metadata (inc. embedded images)
#######################################################################################

import logging
log = logging.getLogger(__name__)

import json

from datetime import datetime
from thirdparty import exiftool


class ExifToolError(Exception):
    pass


def get_metadata_batch(paths):
    """
    Uses exiftool to extract all metadata from files.

    :param paths: list of absolute file paths
    :return: dict of metadata
    """
    metadata = [{}]
    with exiftool.ExifTool(settings.EXIFTOOL) as et:
        metadata = et.get_metadata_batch(paths)
    return metadata


def write_metadata_batch(requests):
    """
    Uses exiftool to write metadata to files.

    :param request: list of dicts in form:
    {
        'path': (string, path to file to write to),
        'metadata':
        {
            'EXIF:Rating': value
        }
    }

    :return:
    """
    print 'requests: %s' % requests
    formatted_requests = []
    # convert each request to list of params in form ["-Rating=5", "-RatingPercent=100", filepath]
    for request in requests:
        args = []
        # if request is setting EXIF:Rating, then conform other rating fields to match
        if "EXIF:Rating" in request['exif']:
            _conform_rating_fields(request['exif'])
        for k, v in request['exif'].iteritems():
            if v is not None:
                args.append("-%s=%s" % (k, str(v)))
        args.append('-overwrite_original_in_place')
        args.append(request['path'])
        formatted_requests.append(args)

    responses = []
    try:
        with exiftool.ExifTool() as et:
            for params in formatted_requests:
                log.debug(' '.join(params))
                response = et.execute(*params)
                if '0 image files updated' in response:
                    raise ExifToolError('Could not write metadata. Cmd = "%s"' % ' '.join(params))
                responses.append([response, params])
    except ExifToolError('Could not write metadata. Cmd = "%s"' % ' '.join(params)):
        pass
    log.debug(responses)
    return responses


def _conform_rating_fields(metadata):
    """
    Checks incoming metadata requests for specific fields that may prompt changing other fields too. For example the
    Rating fields.

    :param metadata: dict in form:
        {
        'EXIF:Rating': value
        }
    :return:
    """
    if "EXIF:Rating" in metadata:
        rating = metadata["EXIF:Rating"]
        rating = str(rating)
        rating_to_percent = {'0': '0', '1': '1', '2': '25', '3': '50', '4': '75', '5': '100'}

        metadata["EXIF:RatingPercent"] = rating_to_percent[rating]
        metadata["XMP:Rating"] = rating
        metadata["XMP:RatingPercent"] = rating_to_percent[rating]


##################################################################
# tests
##################################################################

def main():

    # requests = [{u'url': u'http://192.168.1.112:6500/media/canon_7d2.2018-07-01.038A5058.CR2', u'path': u'canon_7d2.2018-07-01.038A5058.CR2', u'name': u'canon_7d2.2018-07-01.038A5058.CR2', u'metadata': {u'EXIF:Rating': 1, u'EXIF:Model': u'Canon EOS 7D Mark II', u'EXIF:Orientation': u'1', u'EXIF:CreateDate': u'2018:07:01 15:02:49', u'EXIF:ModifyDate': u'2018:07:01 15:02:49'}}]
    requests = [{u'url': u'http://192.168.1.112:6500/media/canon_7d2.2018-07-01.038A5058.CR2',
                 u'path': u'/Users/Home/Pictures/test.cr2', u'name': u'test.cr2',
                 u'exif': {u'EXIF:Rating': 1}}]
    write_metadata_batch(requests)

    #print get_metadata_batch(['/Users/Home/Pictures/test.cr2'])


if __name__ == "__main__":
    main()
