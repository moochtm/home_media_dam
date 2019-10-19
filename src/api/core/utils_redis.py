
from redis import Redis
from rq import Queue

import utils_preview

import logging
log = logging.getLogger(__name__)


def add_preview_task_to_redis(full_path):
    q = Queue('previews', connection=Redis())
    job = q.enqueue(utils_preview.cache_all_preview_images, full_path)
    log.info("Redis Job created: %s " % job.key)


def test_task(full_path, previous_path):
    q = Queue('test', connection=Redis())
    job = q.enqueue(utils_preview.cache_all_preview_images, full_path, previous_path)
    log.info("Redis Job created: %s " % job.key)