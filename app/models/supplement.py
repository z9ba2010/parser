from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class SupplementProduct(Base):
    __tablename__ = "supplement_products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True) # protein, creatine, isotonics, vitamins, omega-3, bcaa, etc.
    form = Column(String(100), nullable=False, index=True) # порошок, капсулы, батончики, жидкость
    
    dosage = Column(String(150), nullable=True) # e.g. "24г белка на порцию"
    serving_size = Column(String(100), nullable=True) # e.g. "30 г (1 мерная ложка)"
    servings_count = Column(Integer, default=30)
    composition = Column(JSON, default=list) # ["Изолят сывороточного белка", "Концентрат"]
    
    target_goals = Column(JSON, default=list) # ["выносливость", "восстановление", "набор массы", "сушка"]
    flavors = Column(JSON, default=list) # ["Шоколад", "Ваниль", "Банан"]
    volume_weight = Column(String(100), nullable=True) # "908 г (2 lbs)"
    
    price = Column(Float, nullable=False, index=True)
    old_price = Column(Float, nullable=True)
    currency = Column(String(10), default="RUB")
    in_stock = Column(Boolean, default=True, index=True)
    
    source = Column(String(100), nullable=False, index=True)
    source_url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=False)
    
    rating = Column(Float, default=4.9)
    reviews_count = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
