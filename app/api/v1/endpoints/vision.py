import httpx
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.vision_service import vision_service
from app.schemas.vision import VisionRecognitionResponse

router = APIRouter(prefix="/vision", tags=["Module 2: Визуальное распознавание товаров (Visual Search)"])

class ImageUrlRequest(BaseModel):
    image_url: str

@router.post(
    "/recognize",
    response_model=VisionRecognitionResponse,
    summary="Распознавание товара по фотографии (камера телефона / файл)"
)
async def recognize_item_by_photo(
    file: UploadFile = File(..., description="Файл изображения кроссовка или экипировки (JPEG/PNG/WebP)"),
    db: Session = Depends(get_db)
):
    """
    Принимает фотографию спортивной обуви или экипировки, сделанную на камеру смартфона.
    
    1. Компьютерное зрение (Gemini Vision API) определяет бренд, модель, цветовую гамму и особенности.
    2. Поисковый алгоритм сопоставляет результаты с базой данных каталога.
    3. Возвращает карточку товара с актуальными ценами на площадках, ссылками на покупку и характеристиками.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Загруженный файл имеет некорректный тип ({file.content_type}). Ожидается изображение."
        )

    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Передан пустой файл изображения."
        )

    # 1. AI Visual Analysis
    detected_features = await vision_service.analyze_image_bytes(
        image_bytes=image_bytes,
        mime_type=file.content_type,
        filename=file.filename or ""
    )

    # 2. Database Catalog Matching
    response = vision_service.match_against_catalog(db=db, detected=detected_features)
    return response

@router.post(
    "/recognize-url",
    response_model=VisionRecognitionResponse,
    summary="Распознавание товара по URL изображения"
)
async def recognize_item_by_url(
    payload: ImageUrlRequest,
    db: Session = Depends(get_db)
):
    """
    Распознавание спортивного товара по внешней ссылке на изображение.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(payload.image_url)
            resp.raise_for_status()
            image_bytes = resp.content
            mime_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Не удалось загрузить изображение по указанной ссылке: {e}"
        )

    detected_features = await vision_service.analyze_image_bytes(
        image_bytes=image_bytes,
        mime_type=mime_type,
        filename=payload.image_url.split("/")[-1]
    )

    response = vision_service.match_against_catalog(db=db, detected=detected_features)
    return response
