from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime

class ApparelBase(BaseModel):
    sku_id: Optional[str] = None
    product_name: Optional[str] = None
    title: str
    brand: str
    category: str # Strict 20 categories
    subcategory: Optional[str] = None
    gender: str # Мужской, Женский, Унисекс
    price_current: float
    price: Optional[float] = None
    old_price: Optional[float] = None
    currency: str = "RUB"
    sizes: List[str] = []
    image_urls: List[str] = []
    image_url: Optional[str] = None
    source_url: str
    source: str
    in_stock: bool = True
    model_name: Optional[str] = None
    purpose: List[str] = []
    color: Optional[str] = None
    technologies: List[str] = []
    specs: Dict[str, Any] = {}
    description: Optional[str] = None
    rating: float = 4.8
    reviews_count: int = 0

    @model_validator(mode="before")
    @classmethod
    def sync_aliases(cls, data: Any):
        if isinstance(data, dict):
            # Sync product_name <-> title
            if "product_name" not in data or not data["product_name"]:
                data["product_name"] = data.get("title", "")
            if "title" not in data or not data["title"]:
                data["title"] = data.get("product_name", "")

            # Sync price_current <-> price
            if "price_current" not in data and "price" in data:
                data["price_current"] = data["price"]
            elif "price" not in data and "price_current" in data:
                data["price"] = data["price_current"]

            # Sync image_urls <-> image_url
            if "image_urls" not in data and "image_url" in data:
                data["image_urls"] = [data["image_url"]] if data["image_url"] else []
            elif "image_url" not in data and "image_urls" in data and data["image_urls"]:
                data["image_url"] = data["image_urls"][0]
        return data

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

class TaxonomyResponse(BaseModel):
    categories: Dict[str, List[str]]
    total_categories: int
