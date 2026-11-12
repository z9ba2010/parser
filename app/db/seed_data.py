import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.apparel import ApparelProduct
from app.models.supplement import SupplementProduct
from app.models.event import SportEvent
from app.parsers.apparel_parser import ApparelCatalogParser
from app.parsers.supplement_parser import SupplementCatalogParser
from app.parsers.events_parser import EventsAggregatorParser

logger = logging.getLogger(__name__)

async def seed_initial_data_if_empty(db: Session):
    """
    Seeds initial catalog data if the database is empty,
    enabling out-of-the-box demonstration of all modules.
    """
    apparel_count = db.query(ApparelProduct).count()
    supplements_count = db.query(SupplementProduct).count()
    events_count = db.query(SportEvent).count()

    if apparel_count == 0:
        logger.info("Seeding apparel catalog...")
        parser = ApparelCatalogParser()
        items = await parser.parse(limit=50)
        parser.save_items(db, items)
        await parser.close()

    if supplements_count == 0:
        logger.info("Seeding supplements catalog...")
        parser = SupplementCatalogParser()
        items = await parser.parse(limit=50)
        parser.save_items(db, items)
        await parser.close()

    if events_count == 0:
        logger.info("Seeding sports events calendar...")
        parser = EventsAggregatorParser()
        items = await parser.parse(limit=50)
        parser.save_items(db, items)
        await parser.close()

    logger.info("Database seeding check completed.")
