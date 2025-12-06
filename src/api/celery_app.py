from celery import Celery
import os

celery_app = Celery(
    "media_tasks",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery_app.conf.task_routes = {
    "tasks.download_media": {"queue": "io"},
    "tasks.process_video": {"queue": "cpu"},
}

celery_app.conf.update(
    broker_connection_retry_on_startup=True,
)

celery_app.conf.worker_concurrency = 4
