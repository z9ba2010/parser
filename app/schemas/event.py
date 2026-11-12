from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class EventBase(BaseModel):
    title: str
    discipline: str # бег, трейл, триатлон, гонки_с_препятствиями, велоспорт, лыжи, фитнес
    start_date: date
    end_date: Optional[date] = None
    city: str
    region: str
    country: str = "Россия"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distances: List[str] = []
    elevation_gain_m: Optional[int] = None
    registration_status: str = "open" # open, closing_soon, sold_out, announced
    registration_link: str
    official_website: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    organizer: Optional[str] = None
    cover_image_url: Optional[str] = None
    description: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    distance_km: Optional[float] = None # Calculated distance if user passed lat/lon
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class EventListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[EventResponse]
