import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from app.core.config import settings

logger = logging.getLogger(__name__)

# Persistent job store using the same database as the app
jobstores = {
    'default': SQLAlchemyJobStore(url=settings.database_url)
}

scheduler = AsyncIOScheduler(jobstores=jobstores)

def start_scheduler():
    if not scheduler.running:
        logger.info("Starting APScheduler...")
        scheduler.start()

def shutdown_scheduler():
    if scheduler.running:
        logger.info("Shutting down APScheduler...")
        scheduler.shutdown()
