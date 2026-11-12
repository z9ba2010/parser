import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.database import SessionLocal
from app.parsers.runner import run_parser_job

logger = logging.getLogger(__name__)

class ParserScheduler:
    """
    Automated background scheduler for periodic parsing, updating prices,
    sizes, and synchronizing new collections.
    """
    def __init__(self):
        self.is_running: bool = False
        self._task: Optional[asyncio.Task] = None
        self.interval_seconds: int = settings.PARSER_INTERVAL_HOURS * 3600
        self.last_run_at: Optional[datetime] = None
        self.next_run_at: Optional[datetime] = None
        self.jobs_executed: int = 0

    def start(self):
        """Starts the background periodic parser loop."""
        if self.is_running:
            logger.info("Scheduler is already running.")
            return

        self.is_running = True
        self.next_run_at = datetime.now(timezone.utc) + timedelta(seconds=self.interval_seconds)
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Parser Scheduler started. Interval: {settings.PARSER_INTERVAL_HOURS}h.")

    def stop(self):
        """Stops the scheduler."""
        if not self.is_running:
            return
        self.is_running = False
        if self._task:
            self._task.cancel()
        logger.info("Parser Scheduler stopped.")

    async def _run_loop(self):
        while self.is_running:
            try:
                await asyncio.sleep(self.interval_seconds)
                logger.info("Executing scheduled periodic parse job...")
                self.last_run_at = datetime.now(timezone.utc)
                self.next_run_at = self.last_run_at + timedelta(seconds=self.interval_seconds)

                with SessionLocal() as db:
                    await run_parser_job(db=db, domain="all", limit=50)

                self.jobs_executed += 1
                logger.info(f"Scheduled parser iteration #{self.jobs_executed} completed successfully.")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error during scheduled parser loop: {e}")
                await asyncio.sleep(60) # Short wait before retry

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "interval_hours": settings.PARSER_INTERVAL_HOURS,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "jobs_executed": self.jobs_executed
        }

parser_scheduler = ParserScheduler()
