"""Celery application configuration."""

import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Redis URL for message broker and result backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "denso_forecast",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.forecast_tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
    },
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max per task
    task_soft_time_limit=1500,  # 25 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    
    # Logging
    worker_hijack_root_logger=False,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
)

# Celery Beat schedule - Run forecast every 2 hours
celery_app.conf.beat_schedule = {
    "run-forecast-every-2-hours": {
        "task": "app.tasks.forecast_tasks.run_scheduled_forecast",
        "schedule": crontab(minute=0, hour="*/2"),  # Every 2 hours at :00
        "args": (),
        "options": {
            "expires": 3600,  # Task expires after 1 hour if not picked up
        },
    },
    # Example: Daily summary at 8 AM
    "daily-forecast-summary": {
        "task": "app.tasks.forecast_tasks.generate_daily_summary",
        "schedule": crontab(hour=8, minute=0),  # Every day at 8:00 AM
        "args": (),
    },
    # Example: Weekly cleanup on Sunday at midnight
    "weekly-cleanup-old-alerts": {
        "task": "app.tasks.forecast_tasks.cleanup_old_alerts",
        "schedule": crontab(hour=0, minute=0, day_of_week=0),  # Sunday 00:00
        "args": (90,),  # Delete alerts older than 90 days
    },
}

# Task routing (optional - for multiple queues)
# DISABLED for now - use default queue for all tasks
# celery_app.conf.task_routes = {
#     "app.tasks.forecast_tasks.run_scheduled_forecast": {"queue": "forecast"},
#     "app.tasks.forecast_tasks.generate_daily_summary": {"queue": "reports"},
#     "app.tasks.forecast_tasks.cleanup_old_alerts": {"queue": "maintenance"},
# }

# Default queue - all tasks use this
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange = "default"
celery_app.conf.task_default_routing_key = "default"


if __name__ == "__main__":
    celery_app.start()
