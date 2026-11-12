import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String

from app.core.database import get_db
from app.models.supplement import SupplementProduct
from app.schemas.supplement import SupplementResponse, SupplementListResponse, SupplementCreate

router = APIRouter(prefix="/supplements", tags=["Module 3: Спортивное питание и БАДы"])

@router.get("", response_model=SupplementListResponse, summary="Поиск и фильтрация спортивного питания и БАДов")
def list_supplements(
    search: Optional[str] = Query(None, description="Поисковый запрос (по названию, бренду, составу)"),
    category: Optional[str] = Query(None, description="Категория (protein, creatine, isotonics, vitamins, omega-3, bcaa)"),
    brand: Optional[str] = Query(None, description="Бренд (Optimum Nutrition, Maxler, SiS, NOW Foods, Olimp)"),
    form: Optional[str] = Query(None, description="Форма выпуска (порошок, капсулы, батончики, жидкость)"),
    target_goal: Optional[str] = Query(None, description="Цель приема (выносливость, восстановление, набор массы, сушка, суставы)"),
    min_price: Optional[float] = Query(None, description="Минимальная цена (руб.)"),
    max_price: Optional[float] = Query(None, description="Максимальная цена (руб.)"),
    in_stock: Optional[bool] = Query(None, description="Только в наличии"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    db: Session = Depends(get_db)
):
    """
    Каталог спортивного питания и БАДов с фильтрацией по целям (набор массы, сушка,
    выносливость, восстановление), форме выпуска, бренду и составу.
    """
    query = db.query(SupplementProduct)

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            or_(
                SupplementProduct.title.ilike(search_fmt),
                SupplementProduct.brand.ilike(search_fmt),
                SupplementProduct.description.ilike(search_fmt)
            )
        )

    if category:
        query = query.filter(SupplementProduct.category.ilike(f"%{category.strip()}%"))

    if brand:
        query = query.filter(SupplementProduct.brand.ilike(f"%{brand.strip()}%"))

    if form:
        query = query.filter(SupplementProduct.form.ilike(f"%{form.strip()}%"))

    if target_goal:
        g_strip = target_goal.strip()
        g_unicode = json.dumps(g_strip).strip('"')
        query = query.filter(
            or_(
                cast(SupplementProduct.target_goals, String).ilike(f"%{g_strip}%"),
                cast(SupplementProduct.target_goals, String).ilike(f"%{g_unicode}%")
            )
        )

    if min_price is not None:
        query = query.filter(SupplementProduct.price >= min_price)

    if max_price is not None:
        query = query.filter(SupplementProduct.price <= max_price)

    if in_stock is not None:
        query = query.filter(SupplementProduct.in_stock == in_stock)

    total = query.count()
    items = query.order_by(SupplementProduct.rating.desc(), SupplementProduct.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return SupplementListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[SupplementResponse.model_validate(s) for s in items]
    )

@router.get("/categories", response_model=List[str], summary="Список категорий БАДов")
def list_categories(db: Session = Depends(get_db)):
    """Возвращает список уникальных категорий питания в каталоге."""
    results = db.query(SupplementProduct.category).distinct().order_by(SupplementProduct.category).all()
    return [r[0] for r in results if r[0]]

@router.get("/goals", response_model=List[str], summary="Список целей приема")
def list_goals():
    """Возвращает стандартные цели приема для фильтрации в мобильных приложениях."""
    return [
        "выносливость",
        "восстановление",
        "набор массы",
        "сушка",
        "суставы",
        "иммунитет",
        "сила"
    ]

@router.get("/{supplement_id}", response_model=SupplementResponse, summary="Карточка БАДа/питания по ID")
def get_supplement(supplement_id: int, db: Session = Depends(get_db)):
    """Получение полной информации о добавке: дозировка, состав, цель приема, цены."""
    item = db.query(SupplementProduct).filter(SupplementProduct.id == supplement_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return SupplementResponse.model_validate(item)

@router.post("", response_model=SupplementResponse, status_code=status.HTTP_201_CREATED, summary="Добавить БАД/питание")
def create_supplement(data: SupplementCreate, db: Session = Depends(get_db)):
    """Эндпоинт для программного добавления спортивного питания."""
    item = SupplementProduct(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return SupplementResponse.model_validate(item)
