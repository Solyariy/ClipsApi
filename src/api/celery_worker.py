from celery import Celery
from src.settings import celery_settings

celery_app = Celery(
    __name__,
    broker=str(celery_settings.BROKER_URL),
    backend=str(celery_settings.RESULT_BACKEND),
)
