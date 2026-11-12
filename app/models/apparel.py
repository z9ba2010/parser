from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class ApparelProduct(Base):
    __tablename__ = "apparel_products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Required attributes from Technical Specification
    sku_id = Column(String(100), index=True, nullable=True) # Уникальный артикул на стороне источника
    product_name = Column(String(255), nullable=True, index=True) # Полное наименование модели
    title = Column(String(255), nullable=False, index=True) # Совместимость с общим каталогом
    brand = Column(String(100), nullable=False, index=True) # Нормализованный бренд (п. 3)
    category = Column(String(100), nullable=False, index=True) # Строгая таксономия (20 категорий)
    subcategory = Column(String(100), nullable=True, index=True)
    gender = Column(String(50), nullable=False, index=True) # Мужской / Женский / Унисекс
    
    price_current = Column(Float, nullable=False, index=True) # Текущая цена
    price = Column(Float, nullable=False, default=0.0) # Синоним для обратной совместимости
    old_price = Column(Float, nullable=True)
    currency = Column(String(10), default="RUB")
    
    sizes = Column(JSON, default=list) # Доступные размеры
    image_urls = Column(JSON, default=list) # Массив ссылок на фото в высоком разрешении (для Vision)
    image_url = Column(Text, nullable=True) # Основное превью фото
    gallery = Column(JSON, default=list)
    
    source_url = Column(Text, nullable=False) # Ссылка на страницу товара
    source = Column(String(100), nullable=False, index=True)
    in_stock = Column(Boolean, default=True, index=True)
    
    model_name = Column(String(150), nullable=True, index=True)
    purpose = Column(JSON, default=list)
    color = Column(String(150), nullable=True)
    technologies = Column(JSON, default=list)
    specs = Column(JSON, default=dict)
    description = Column(Text, nullable=True)
    rating = Column(Float, default=4.8)
    reviews_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
