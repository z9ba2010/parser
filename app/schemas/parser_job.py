from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ParserTriggerRequest(BaseModel):
    domain: str = "apparel" # apparel, supplements, events, all
    category: Optional[str] = None # Optional specific category from the 20 target categories
    limit_per_source: int = 50

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

class ProxyStatusResponse(BaseModel):
    total_proxies: int
    healthy_proxies: int
    failed_proxies: int
    active_proxies: List[str]

class AddProxyRequest(BaseModel):
    proxy_url: str

class SchedulerStatusResponse(BaseModel):
    is_running: bool
    interval_hours: int
    last_run_at: Optional[str] = None
    next_run_at: Optional[str] = None
    jobs_executed: int
