import logging
import sys
from threading import Lock

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.schedulers import SchedulerNotRunningError
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
except ModuleNotFoundError:  # pragma: no cover - optional dependency in tests/dev
    SQLAlchemyJobStore = None
    SchedulerNotRunningError = RuntimeError
    AsyncIOScheduler = None

# Persistent job store using the same database as the app.
scheduler = None
if AsyncIOScheduler is not None and SQLAlchemyJobStore is not None:
    jobstores = {"default": SQLAlchemyJobStore(url=settings.database_url)}
    scheduler = AsyncIOScheduler(jobstores=jobstores)
_scheduler_lock = Lock()


def start_scheduler():
    if "pytest" in sys.modules or scheduler is None:
        if scheduler is None:
            logger.info("APScheduler unavailable; scheduler startup skipped.")
        return
    with _scheduler_lock:
        if not scheduler.running:
            logger.info("Starting APScheduler...")
            scheduler.start()


def shutdown_scheduler():
    if "pytest" in sys.modules or scheduler is None:
        return
    with _scheduler_lock:
        if scheduler.running:
            logger.info("Shutting down APScheduler...")
            try:
                scheduler.shutdown()
            except SchedulerNotRunningError:
                logger.debug("APScheduler already stopped during concurrent shutdown.")
