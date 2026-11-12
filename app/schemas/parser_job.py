from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ParserTriggerRequest(BaseModel):
    domain: str = "all" # apparel, supplements, events, all
    limit_per_source: int = 20

class ParserJobResponse(BaseModel):
    id: int
    job_id: str
    domain: str
    status: str
    items_scanned: int
    items_added: int
    items_updated: int
    errors_count: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ParserJobListResponse(BaseModel):
    total: int
    items: List[ParserJobResponse]
