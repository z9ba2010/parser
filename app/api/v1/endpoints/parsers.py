from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.parser_job import ParserJob
from app.schemas.parser_job import ParserJobResponse, ParserJobListResponse, ParserTriggerRequest
from app.parsers.runner import run_parser_job

router = APIRouter(prefix="/parsers", tags=["Парсеры и сбор данных"])

@router.post(
    "/run",
    response_model=ParserJobResponse,
    summary="Запуск парсинга данных (одежда, БАДы, события или всё вместе)"
)
async def trigger_parser(
    payload: ParserTriggerRequest,
    db: Session = Depends(get_db)
):
    """
    Запускает мультидоменный сбор данных:
    - `domain`: 'apparel' (экипировка/обувь), 'supplements' (БАДы/питание), 'events' (спортивные события) или 'all'.
    - `limit_per_source`: количество записей для парсинга.
    """
    if payload.domain not in ("apparel", "supplements", "events", "all"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный domain. Допустимые значения: 'apparel', 'supplements', 'events', 'all'"
        )

    job = await run_parser_job(db=db, domain=payload.domain, limit=payload.limit_per_source)
    return ParserJobResponse.model_validate(job)

@router.get(
    "/jobs",
    response_model=ParserJobListResponse,
    summary="Журнал и статус задач парсинга"
)
def list_parser_jobs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Возвращает историю выполнения задач парсинга со статусами и количеством собранных элементов."""
    total = db.query(ParserJob).count()
    jobs = db.query(ParserJob).order_by(ParserJob.id.desc()).limit(limit).all()
    return ParserJobListResponse(
        total=total,
        items=[ParserJobResponse.model_validate(j) for j in jobs]
    )

@router.get(
    "/jobs/{job_id}",
    response_model=ParserJobResponse,
    summary="Детали задачи парсинга по job_id"
)
def get_parser_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Получение детальной информации о конкретной задаче парсинга."""
    job = db.query(ParserJob).filter(ParserJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача парсинга не найдена")
    return ParserJobResponse.model_validate(job)
