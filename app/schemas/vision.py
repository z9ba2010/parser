from typing import List, Optional
from pydantic import BaseModel
from app.schemas.apparel import ApparelResponse

class VisionDetectedFeatures(BaseModel):
    brand: Optional[str] = None
    model_name: Optional[str] = None
    category: Optional[str] = "shoes" # shoes, clothing, accessories
    subcategory: Optional[str] = "кроссовки"
    colorway: Optional[str] = None
    visual_traits: List[str] = []
    confidence_score: float = 0.0
    description: Optional[str] = None

class VisionRecognitionResponse(BaseModel):
    detected: VisionDetectedFeatures
    matched_product: Optional[ApparelResponse] = None
    similar_products: List[ApparelResponse] = []
    search_query_used: str
    recognition_engine: str
    note: Optional[str] = None
