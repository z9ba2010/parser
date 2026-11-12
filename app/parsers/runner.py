import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.parser_job import ParserJob
from app.parsers.apparel_parser import ApparelCatalogParser
from app.parsers.supplement_parser import SupplementCatalogParser
from app.parsers.events_parser import EventsAggregatorParser

logger = logging.getLogger(__name__)

async def run_parser_job(db: Session, domain: str = "all", limit: int = 50, category: Optional[str] = None) -> ParserJob:
    """
    Executes a parsing job across requested domains, updates ParserJob audit log in database.
    """
    job_id = f"job-{uuid.uuid4().hex[:12]}"
    job_domain = f"{domain}:{category}" if category else domain
    job = ParserJob(
        job_id=job_id,
        domain=job_domain,
        status="running",
        items_scanned=0,
        items_added=0,
        items_updated=0,
        errors_count=0,
        started_at=datetime.now(timezone.utc)
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        total_scanned = 0
        total_added = 0
        total_updated = 0

        # Domain: apparel
        if domain in ("apparel", "all"):
            apparel_parser = ApparelCatalogParser()
            try:
                items = await apparel_parser.parse(limit=limit, target_category=category)
                res = apparel_parser.save_items(db, items)
                total_scanned += res["scanned"]
                total_added += res["added"]
                total_updated += res["updated"]
            finally:
                await apparel_parser.close()

        # Domain: supplements
        if domain in ("supplements", "all"):
            supp_parser = SupplementCatalogParser()
            try:
                items = await supp_parser.parse(limit=limit)
                res = supp_parser.save_items(db, items)
                total_scanned += res["scanned"]
                total_added += res["added"]
                total_updated += res["updated"]
            finally:
                await supp_parser.close()

        # Domain: events
        if domain in ("events", "all"):
            events_parser = EventsAggregatorParser()
            try:
                items = await events_parser.parse(limit=limit)
                res = events_parser.save_items(db, items)
                total_scanned += res["scanned"]
                total_added += res["added"]
                total_updated += res["updated"]
            finally:
                await events_parser.close()

        job.status = "completed"
        job.items_scanned = total_scanned
        job.items_added = total_added
        job.items_updated = total_updated
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        logger.info(f"Parser job {job_id} completed: scanned={total_scanned}, added={total_added}, updated={total_updated}")

    except Exception as e:
        logger.exception(f"Parser job {job_id} failed with error: {e}")
        job.status = "failed"
        job.errors_count = 1
        job.error_message = str(e)
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

    return job
