from celery import Celery
from src.settings import celery_settings

celery_app = Celery(
    __name__,
    broker=str(celery_settings.BROKER_URL),
    backend=str(celery_settings.RESULT_BACKEND),
)

task_queues = {
    "downloads_queue": {},
    "group_and_process_queue": {},
    "video_processing_queue": {},
}

task_routes = {
    "cleanup_dir_task": {"queue": "group_and_process_queue"},
    "download_files_task": {"queue": "downloads_queue"},
    "group_and_process_task": {"queue": "group_and_process_queue"},
    "process_setup_task": {"queue": "video_processing_queue"},
}

celery_app.autodiscover_tasks([
    "src.api",
])

celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.task_acks_late = True

celery_app.conf.task_routes = task_routes
