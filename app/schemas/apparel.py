from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ApparelBase(BaseModel):
    title: str
    brand: str
    model_name: str
    category: str # shoes, clothing, accessories
    subcategory: str # кроссовки, тайтсы, куртки
    gender: str # men, women, unisex
    purpose: List[str] = []
    sizes: List[str] = []
    color: Optional[str] = None
    price: float
    old_price: Optional[float] = None
    currency: str = "RUB"
    in_stock: bool = True
    source: str
    source_url: str
    image_url: str
    gallery: List[str] = []
    technologies: List[str] = []
    specs: Dict[str, Any] = {}
    description: Optional[str] = None
    rating: float = 4.8
    reviews_count: int = 0

class ApparelCreate(ApparelBase):
    pass

class ApparelResponse(ApparelBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ApparelListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ApparelResponse]
