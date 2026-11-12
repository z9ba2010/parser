from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, Date
from datetime import datetime, timezone
from app.core.database import Base

class SportEvent(Base):
    __tablename__ = "sport_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    discipline = Column(String(100), nullable=False, index=True) # бег, трейл, триатлон, гонки_с_препятствиями, велоспорт, лыжи, фитнес
    
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=True)
    
    city = Column(String(100), nullable=False, index=True)
    region = Column(String(150), nullable=False, index=True)
    country = Column(String(100), default="Россия", index=True)
    
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    
    distances = Column(JSON, default=list) # ["10 км", "21.1 км", "42.2 км"]
    elevation_gain_m = Column(Integer, nullable=True) # набор высоты в метрах
    
    registration_status = Column(String(50), default="open", index=True) # open, closing_soon, sold_out, announced
    registration_link = Column(Text, nullable=False)
    official_website = Column(Text, nullable=True)
    
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    organizer = Column(String(150), nullable=True, index=True)
    
    cover_image_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
