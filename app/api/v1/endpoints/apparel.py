import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String

from app.core.database import get_db
from app.models.apparel import ApparelProduct
from app.schemas.apparel import ApparelResponse, ApparelListResponse, ApparelCreate

router = APIRouter(prefix="/apparel", tags=["Module 1: Спортивная одежда и обувь"])

@router.get("", response_model=ApparelListResponse, summary="Поиск и фильтрация одежды/обуви")
def list_apparel(
    search: Optional[str] = Query(None, description="Поисковый запрос (по названию, модели, бренду, описанию)"),
    brand: Optional[str] = Query(None, description="Бренд (Nike, Adidas, Salomon, Hoka, Asics, Puma и др.)"),
    category: Optional[str] = Query(None, description="Категория (shoes, clothing, accessories)"),
    subcategory: Optional[str] = Query(None, description="Подкатегория (кроссовки, шиповки, тайтсы, куртки)"),
    gender: Optional[str] = Query(None, description="Пол (men, women, unisex)"),
    purpose: Optional[str] = Query(None, description="Назначение (бег, трейл, кроссфит, фитнес, шоссе)"),
    min_price: Optional[float] = Query(None, description="Минимальная цена (руб.)"),
    max_price: Optional[float] = Query(None, description="Максимальная цена (руб.)"),
    in_stock: Optional[bool] = Query(None, description="Только в наличии"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    db: Session = Depends(get_db)
):
    """
    Каталог спортивной обуви и экипировки с гибкой фильтрацией по бренду, типу,
    назначению (бег, трейл, кроссфит), размерной сетке и цене.
    """
    query = db.query(ApparelProduct)

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ApparelProduct.title.ilike(search_fmt),
                ApparelProduct.model_name.ilike(search_fmt),
                ApparelProduct.brand.ilike(search_fmt),
                ApparelProduct.description.ilike(search_fmt)
            )
        )

    if brand:
        query = query.filter(ApparelProduct.brand.ilike(f"%{brand.strip()}%"))

    if category:
        query = query.filter(ApparelProduct.category == category)

    if subcategory:
        query = query.filter(ApparelProduct.subcategory.ilike(f"%{subcategory.strip()}%"))

    if gender:
        query = query.filter(ApparelProduct.gender == gender)

    if purpose:
        p_strip = purpose.strip()
        p_unicode = json.dumps(p_strip).strip('"')
        query = query.filter(
            or_(
                cast(ApparelProduct.purpose, String).ilike(f"%{p_strip}%"),
                cast(ApparelProduct.purpose, String).ilike(f"%{p_unicode}%")
            )
        )

    if min_price is not None:
        query = query.filter(ApparelProduct.price >= min_price)

    if max_price is not None:
        query = query.filter(ApparelProduct.price <= max_price)

    if in_stock is not None:
        query = query.filter(ApparelProduct.in_stock == in_stock)

    total = query.count()
    items = query.order_by(ApparelProduct.rating.desc(), ApparelProduct.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return ApparelListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ApparelResponse.model_validate(p) for p in items]
    )

@router.get("/brands", response_model=List[str], summary="Список доступных брендов")
def list_brands(db: Session = Depends(get_db)):
    """Возвращает список уникальных брендов в каталоге."""
    results = db.query(ApparelProduct.brand).distinct().order_by(ApparelProduct.brand).all()
    return [r[0] for r in results if r[0]]

@router.get("/{product_id}", response_model=ApparelResponse, summary="Карточка товара по ID")
def get_apparel(product_id: int, db: Session = Depends(get_db)):
    """Получение полной карточки товара со всеми характеристиками, размерами и ценами."""
    product = db.query(ApparelProduct).filter(ApparelProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return ApparelResponse.model_validate(product)

@router.post("", response_model=ApparelResponse, status_code=status.HTTP_201_CREATED, summary="Добавить товар вручную")
def create_apparel(data: ApparelCreate, db: Session = Depends(get_db)):
    """Эндпоинт для программного добавления товара в каталог."""
    product = ApparelProduct(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return ApparelResponse.model_validate(product)
