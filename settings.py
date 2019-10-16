
# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# API settings
HOMEMEDIA_ROOT = '/Users/Home/Pictures'
HOMEMEDIA_INBOX = '_inbox'
HOMEMEDIA_ARCHIVE = 'ORIGINALS'
MEDIA_FILE_EXTENSIONS = ['.JPG','.JPEG','.CR2','.MOV','.MP4', '.DNG', '.HEIC']
FOLDER_PREFIX_BLACKLIST = ['.','@','Lightroom']
IMAGE_CACHE_PATH = '/Users/home/Sites/preview'
IMAGE_TRASH_PATH = '/Users/Home/.homemedia_api/trash'

PREVIEW_MIN_RES = 400
PREVIEW_MAX_RES = 1920

# exiftool settings
EXIFTOOL = 'exiftool'

# ffmpeg settings
FFMPEG = 'ffmpeg'

# ImageMagick settings
CONVERT = 'convert'

# Flask settings
# API_FLASK_SERVER_HOST = '127.0.0.1'
API_FLASK_SERVER_HOST = '192.168.1.70'
API_FLASK_SERVER_PORT = 6500
API_FLASK_DEBUG = True  # Do not use debug mode in production

API_INITIAL_RESOURCE = 'browse'
API_INITIAL_QUERY = 'path=%s&include_assets=true&flatten_folders=false' % HOMEMEDIA_INBOX