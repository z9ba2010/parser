from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.event import SportEvent
from app.schemas.event import EventResponse, EventListResponse, EventCreate
from app.services.geo_service import calculate_haversine_distance_km, calculate_bounding_box

router = APIRouter(prefix="/events", tags=["Module 4: Агрегатор спортивных событий РФ"])

@router.get("", response_model=EventListResponse, summary="Календарь спортивных событий с гео-фильтром")
def list_events(
    search: Optional[str] = Query(None, description="Поисковый запрос (по названию, организатору, городу)"),
    discipline: Optional[str] = Query(None, description="Дисциплина (бег, трейл, триатлон, гонки_с_препятствиями, велоспорт, фитнес)"),
    city: Optional[str] = Query(None, description="Город (Москва, Сочи, Суздаль, Казань и др.)"),
    region: Optional[str] = Query(None, description="Регион РФ (Московская область, Краснодарский край и др.)"),
    date_from: Optional[date] = Query(None, description="Дата старта 'ОТ' (ГГГГ-ММ-ДД)"),
    date_to: Optional[date] = Query(None, description="Дата старта 'ДО' (ГГГГ-ММ-ДД)"),
    registration_status: Optional[str] = Query(None, description="Статус регистрации (open, closing_soon, sold_out, announced)"),
    lat: Optional[float] = Query(None, description="Гео-широта пользователя для поиска стартов рядом"),
    lon: Optional[float] = Query(None, description="Гео-долгота пользователя для поиска стартов рядом"),
    radius_km: Optional[float] = Query(None, ge=1, le=2000, description="Радиус поиска в километрах (например, 200 км)"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    db: Session = Depends(get_db)
):
    """
    Единый агрегатор спортивных событий по всей России с возможностью гео-поиска
    (события в радиусе N км от пользователя) и фильтрацией по дисциплинам и датам.
    """
    query = db.query(SportEvent)

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            or_(
                SportEvent.title.ilike(search_fmt),
                SportEvent.city.ilike(search_fmt),
                SportEvent.region.ilike(search_fmt),
                SportEvent.organizer.ilike(search_fmt),
                SportEvent.description.ilike(search_fmt)
            )
        )

    if discipline:
        query = query.filter(SportEvent.discipline.ilike(f"%{discipline.strip()}%"))

    if city:
        query = query.filter(SportEvent.city.ilike(f"%{city.strip()}%"))

    if region:
        query = query.filter(SportEvent.region.ilike(f"%{region.strip()}%"))

    if date_from:
        query = query.filter(SportEvent.start_date >= date_from)

    if date_to:
        query = query.filter(SportEvent.start_date <= date_to)

    if registration_status:
        query = query.filter(SportEvent.registration_status == registration_status)

    # Geo Bounding Box pre-filter if coordinates and radius provided
    if lat is not None and lon is not None and radius_km is not None:
        min_lat, max_lat, min_lon, max_lon = calculate_bounding_box(lat, lon, radius_km)
        query = query.filter(
            SportEvent.latitude.isnot(None),
            SportEvent.longitude.isnot(None),
            SportEvent.latitude.between(min_lat, max_lat),
            SportEvent.longitude.between(min_lon, max_lon)
        )

    all_matches = query.order_by(SportEvent.start_date.asc()).all()

    # If geo query, calculate exact haversine distances and filter/sort
    result_items = []
    if lat is not None and lon is not None:
        for event in all_matches:
            if event.latitude is not None and event.longitude is not None:
                dist = calculate_haversine_distance_km(lat, lon, event.latitude, event.longitude)
                if radius_km is None or dist <= radius_km:
                    item_resp = EventResponse.model_validate(event)
                    item_resp.distance_km = dist
                    result_items.append(item_resp)
        result_items.sort(key=lambda x: (x.distance_km if x.distance_km is not None else 999999, x.start_date))
    else:
        result_items = [EventResponse.model_validate(e) for e in all_matches]

    total = len(result_items)
    paginated_items = result_items[(page - 1) * page_size : page * page_size]

    return EventListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=paginated_items
    )

@router.get("/disciplines", response_model=List[str], summary="Список спортивных дисциплин")
def list_disciplines(db: Session = Depends(get_db)):
    """Возвращает список уникальных дисциплин событий (бег, трейл, триатлон, OCR и др.)."""
    results = db.query(SportEvent.discipline).distinct().order_by(SportEvent.discipline).all()
    return [r[0] for r in results if r[0]]

@router.get("/regions", response_model=List[str], summary="Список регионов РФ с событиями")
def list_regions(db: Session = Depends(get_db)):
    """Возвращает список регионов проведения соревнований."""
    results = db.query(SportEvent.region).distinct().order_by(SportEvent.region).all()
    return [r[0] for r in results if r[0]]

@router.get("/{event_id}", response_model=EventResponse, summary="Детали спортивного события по ID")
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Получение полной информации о старте: дистанции, набор высоты, ссылка на регистрацию, организатор."""
    event = db.query(SportEvent).filter(SportEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Спортивное событие не найдено")
    return EventResponse.model_validate(event)

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED, summary="Добавить спортивное событие")
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    """Эндпоинт для добавления спортивного события."""
    event = SportEvent(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventResponse.model_validate(event)
