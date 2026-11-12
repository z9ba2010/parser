from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.parser_job import ParserJob
from app.schemas.parser_job import (
    ParserJobResponse,
    ParserJobListResponse,
    ParserTriggerRequest,
    ProxyStatusResponse,
    AddProxyRequest,
    SchedulerStatusResponse
)
from app.parsers.runner import run_parser_job
from app.core.proxy_manager import proxy_manager
from app.services.scheduler import parser_scheduler

router = APIRouter(prefix="/parsers", tags=["Инфраструктура парсинга и автоматизация"])

@router.post(
    "/run",
    response_model=ParserJobResponse,
    summary="Запуск парсинга данных (с поддержкой выбора категории и ротации IP)"
)
async def trigger_parser(
    payload: ParserTriggerRequest,
    db: Session = Depends(get_db)
):
    """
    Запускает сбор данных:
    - `domain`: 'apparel' (экипировка/обувь), 'supplements' (БАДы/питание), 'events' (спортивные события) или 'all'.
    - `category`: Опциональный фильтр по одной из 20 целевых категорий беговой экипировки.
    - `limit_per_source`: Количество записей для парсинга.
    """
    if payload.domain not in ("apparel", "supplements", "events", "all"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный domain. Допустимые значения: 'apparel', 'supplements', 'events', 'all'"
        )

    job = await run_parser_job(
        db=db,
        domain=payload.domain,
        limit=payload.limit_per_source,
        category=payload.category
    )
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

@router.get(
    "/proxies",
    response_model=ProxyStatusResponse,
    summary="Состояние пула прокси-серверов и ротации IP"
)
def get_proxy_status():
    """
    Возвращает информацию о текущем пуле прокси (например, Proxy6),
    количестве активных и здоровых IP адресов.
    """
    status_data = proxy_manager.get_status()
    return ProxyStatusResponse(**status_data)

@router.post(
    "/proxies",
    response_model=ProxyStatusResponse,
    summary="Добавить прокси-сервер в пул ротации"
)
def add_proxy(payload: AddProxyRequest):
    """
    Добавляет прокси в формате HTTP или SOCKS5 (например, http://login:pass@ip:port).
    """
    proxy_manager.add_proxy(payload.proxy_url)
    return ProxyStatusResponse(**proxy_manager.get_status())

@router.get(
    "/scheduler",
    response_model=SchedulerStatusResponse,
    summary="Статус планировщика автоматического сбора по расписанию"
)
def get_scheduler_status():
    """Возвращает статус автоматического запуска парсеров по расписанию."""
    return SchedulerStatusResponse(**parser_scheduler.get_status())

@router.post(
    "/scheduler/toggle",
    response_model=SchedulerStatusResponse,
    summary="Включить / приостановить фоновое расписание парсинга"
)
def toggle_scheduler(enable: bool = Query(..., description="True для запуска, False для паузы")):
    """Управление фоновым планировщиком обновления цен и коллекций."""
    if enable:
        parser_scheduler.start()
    else:
        parser_scheduler.stop()
    return SchedulerStatusResponse(**parser_scheduler.get_status())
