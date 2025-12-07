from celery import Celery
import time

from src.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)


@celery_app.task(name="create_task")
def create_task(a, b, c):
    time.sleep(a)
    return b + c


