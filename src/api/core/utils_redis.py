
from redis import Redis
from rq import Queue

import utils_preview

import logging
log = logging.getLogger(__name__)


def add_preview_task_to_redis(full_path):
    q = Queue('previews', connection=Redis())
    result = q.enqueue(utils_preview.cache_all_preview_images, full_path)
