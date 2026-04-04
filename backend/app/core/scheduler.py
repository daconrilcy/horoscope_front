import logging
import sys
from threading import Lock

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers import SchedulerNotRunningError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings

logger = logging.getLogger(__name__)

# Persistent job store using the same database as the app
jobstores = {
    'default': SQLAlchemyJobStore(url=settings.database_url)
}

scheduler = AsyncIOScheduler(jobstores=jobstores)
_scheduler_lock = Lock()

def start_scheduler():
    if "pytest" in sys.modules:
        return
    with _scheduler_lock:
        if not scheduler.running:
            logger.info("Starting APScheduler...")
            scheduler.start()

def shutdown_scheduler():
    if "pytest" in sys.modules:
        return
    with _scheduler_lock:
        if scheduler.running:
            logger.info("Shutting down APScheduler...")
            try:
                scheduler.shutdown()
            except SchedulerNotRunningError:
                logger.debug("APScheduler already stopped during concurrent shutdown.")
