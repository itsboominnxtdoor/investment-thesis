from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery("thesis_engine", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "check-for-new-filings": {
        "task": "app.tasks.quarterly_ingestion.check_for_new_filings",
        "schedule": crontab(minute=0),  # Every hour
    },
}

celery_app.autodiscover_tasks(["app.tasks"])
