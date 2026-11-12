import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String

from app.core.database import get_db
from app.models.apparel import ApparelProduct
from app.schemas.apparel import ApparelResponse, ApparelListResponse, ApparelCreate, TaxonomyResponse
from app.services.sanitizer import sanitizer, TAXONOMY_CATEGORIES, CANONICAL_CATEGORIES

router = APIRouter(prefix="/apparel", tags=["Module 1: Спортивная одежда и обувь"])

@router.get("", response_model=ApparelListResponse, summary="Поиск и фильтрация экипировки")
def list_apparel(
    search: Optional[str] = Query(None, description="Поиск по названию, артикулу SKU, модели, бренду"),
    sku_id: Optional[str] = Query(None, description="Поиск по точному артикулу (SKU ID)"),
    category: Optional[str] = Query(None, description="Целевая категория из таксономии (например, 'Обувь', 'Носки', 'Тайтсы')"),
    brand: Optional[str] = Query(None, description="Бренд (Nike, Adidas, Salomon, Asics, Brooks, Hoka и др.)"),
    gender: Optional[str] = Query(None, description="Пол (Мужской, Женский, Унисекс)"),
    purpose: Optional[str] = Query(None, description="Назначение (бег, трейл, кроссфит, шоссе)"),
    min_price: Optional[float] = Query(None, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, description="Максимальная цена"),
    in_stock: Optional[bool] = Query(None, description="Только в наличии"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Количество на странице"),
    db: Session = Depends(get_db)
):
    """
    Каталог беговой экипировки со строгой таксономией 20 категорий и нормализованными брендами.
    """
    query = db.query(ApparelProduct)

    if sku_id:
        query = query.filter(ApparelProduct.sku_id.ilike(f"%{sku_id.strip()}%"))

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ApparelProduct.title.ilike(search_fmt),
                ApparelProduct.product_name.ilike(search_fmt),
                ApparelProduct.sku_id.ilike(search_fmt),
                ApparelProduct.model_name.ilike(search_fmt),
                ApparelProduct.brand.ilike(search_fmt),
                ApparelProduct.description.ilike(search_fmt)
            )
        )

    if brand:
        clean_brand = sanitizer.normalize_brand(brand)
        query = query.filter(
            or_(
                ApparelProduct.brand.ilike(f"%{clean_brand}%"),
                ApparelProduct.brand.ilike(f"%{brand.strip()}%")
            )
        )

    if category:
        clean_cat = sanitizer.normalize_category(category)
        query = query.filter(ApparelProduct.category == clean_cat)

    if gender:
        clean_gender = sanitizer.normalize_gender(gender)
        query = query.filter(ApparelProduct.gender == clean_gender)

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
        query = query.filter(ApparelProduct.price_current >= min_price)

    if max_price is not None:
        query = query.filter(ApparelProduct.price_current <= max_price)

    if in_stock is not None:
        query = query.filter(ApparelProduct.in_stock == in_stock)

    total = query.count()
    items = query.order_by(ApparelProduct.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return ApparelListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ApparelResponse.model_validate(p) for p in items]
    )

@router.get("/taxonomy", response_model=TaxonomyResponse, summary="Таксономия категорий и брендов (п. 3 ТЗ)")
def get_taxonomy():
    """
    Возвращает строгую таксономию 20 категорий и список целевых брендов для каждой.
    """
    return TaxonomyResponse(
        categories=TAXONOMY_CATEGORIES,
        total_categories=len(TAXONOMY_CATEGORIES)
    )

@router.get("/categories", response_model=List[str], summary="Список 20 целевых категорий")
def list_categories():
    """Возвращает список 20 канонических категорий беговой экипировки."""
    return CANONICAL_CATEGORIES

@router.get("/brands", response_model=List[str], summary="Список нормализованных брендов в каталоге")
def list_brands(db: Session = Depends(get_db)):
    """Возвращает уникальные нормализованные бренды товаров из базы."""
    results = db.query(ApparelProduct.brand).distinct().order_by(ApparelProduct.brand).all()
    return [r[0] for r in results if r[0]]

@router.get("/{product_id}", response_model=ApparelResponse, summary="Карточка товара по ID")
def get_apparel(product_id: int, db: Session = Depends(get_db)):
    """Получение полной карточки товара (включая массив фото image_urls, артикул sku_id, размеры и цены)."""
    product = db.query(ApparelProduct).filter(ApparelProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return ApparelResponse.model_validate(product)

@router.post("", response_model=ApparelResponse, status_code=status.HTTP_201_CREATED, summary="Добавить товар с авто-нормализацией")
def create_apparel(data: ApparelCreate, db: Session = Depends(get_db)):
    """
    Добавление товара с автоматической очисткой (Sanitization):
    нормализация имени бренда, строгая привязка категории и пола.
    """
    item_dict = data.model_dump()
    item_dict["brand"] = sanitizer.normalize_brand(item_dict.get("brand"))
    item_dict["category"] = sanitizer.normalize_category(item_dict.get("category"), item_dict.get("title", ""))
    item_dict["gender"] = sanitizer.normalize_gender(item_dict.get("gender"), item_dict.get("title", ""))
    
    if not item_dict.get("price_current"):
        item_dict["price_current"] = item_dict.get("price", 0.0)
    item_dict["price"] = item_dict["price_current"]

    product = ApparelProduct(**item_dict)
    db.add(product)
    db.commit()
    db.refresh(product)
    return ApparelResponse.model_validate(product)
