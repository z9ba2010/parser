from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class ApparelProduct(Base):
    __tablename__ = "apparel_products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    model_name = Column(String(150), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True) # shoes, clothing, accessories
    subcategory = Column(String(100), nullable=False, index=True) # кроссовки, шиповки, тайтсы, куртки
    gender = Column(String(50), nullable=False, index=True) # men, women, unisex
    
    purpose = Column(JSON, default=list) # ["бег", "марафон", "шоссе"]
    sizes = Column(JSON, default=list) # ["40 EU", "41 EU", "42 EU", "43 EU"]
    color = Column(String(150), nullable=True)
    
    price = Column(Float, nullable=False, index=True)
    old_price = Column(Float, nullable=True)
    currency = Column(String(10), default="RUB")
    in_stock = Column(Boolean, default=True, index=True)
    
    source = Column(String(100), nullable=False, index=True)
    source_url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=False)
    gallery = Column(JSON, default=list)
    
    technologies = Column(JSON, default=list) # ["ZoomX", "Flyknit", "Continental"]
    specs = Column(JSON, default=dict) # {"drop_mm": 10, "weight_g": 260, "membrane": "Gore-Tex"}
    description = Column(Text, nullable=True)
    rating = Column(Float, default=4.8)
    reviews_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
