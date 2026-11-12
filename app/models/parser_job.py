from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class ParserJob(Base):
    __tablename__ = "parser_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String(64), unique=True, index=True, nullable=False)
    domain = Column(String(50), nullable=False, index=True) # apparel, supplements, events, all
    status = Column(String(50), default="running", index=True) # running, completed, failed
    
    items_scanned = Column(Integer, default=0)
    items_added = Column(Integer, default=0)
    items_updated = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
