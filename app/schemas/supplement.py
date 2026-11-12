from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SupplementBase(BaseModel):
    title: str
    brand: str
    category: str # protein, creatine, isotonics, vitamins, omega-3, bcaa, preworkout, etc.
    form: str # порошок, капсулы, батончики, жидкость
    dosage: Optional[str] = None
    serving_size: Optional[str] = None
    servings_count: int = 30
    composition: List[str] = []
    target_goals: List[str] = [] # набор массы, выносливость, восстановление, сушка, суставы
    flavors: List[str] = []
    volume_weight: Optional[str] = None
    price: float
    old_price: Optional[float] = None
    currency: str = "RUB"
    in_stock: bool = True
    source: str
    source_url: str
    image_url: str
    rating: float = 4.9
    reviews_count: int = 0
    description: Optional[str] = None

class SupplementCreate(SupplementBase):
    pass

class SupplementResponse(SupplementBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class SupplementListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[SupplementResponse]
