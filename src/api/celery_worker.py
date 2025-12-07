from celery import Celery
import time

from src.settings import celery_settings

celery_app = Celery(
    __name__,
    broker=celery_settings.BROKER_URL,
    backend=celery_settings.RESULT_BACKEND,
)


@celery_app.task(name="create_task")
def create_task(a, b, c):
    time.sleep(a)
    return b + c


