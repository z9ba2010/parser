import logging
from typing import List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from app.parsers.base import BaseParser
from app.models.event import SportEvent

logger = logging.getLogger(__name__)

class EventsAggregatorParser(BaseParser):
    def __init__(self):
        super().__init__(name="EventsAggregatorParser", source="Russia Sports Events Network")

    async def parse(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Parses major sports events across Russian regions:
        Marathons, Trail running, Triathlon, OCR (Гонка Героев), Cycling, Fitness.
        """
        logger.info(f"[{self.name}] Starting sports events aggregation (limit={limit})...")

        sample_events = [
            {
                "title": "Московский Марафон 2026",
                "discipline": "бег",
                "start_date": date(2026, 9, 20),
                "end_date": date(2026, 9, 20),
                "city": "Москва",
                "region": "г. Москва",
                "country": "Россия",
                "latitude": 55.7158, # Лужники
                "longitude": 37.5537,
                "distances": ["42.2 км", "10 км", "Корпоративная эстафета"],
                "elevation_gain_m": 120,
                "registration_status": "open",
                "registration_link": "https://moscowmarathon.runc.run/",
                "official_website": "https://runc.run/",
                "min_price": 3500.0,
                "max_price": 6500.0,
                "organizer": "Беговое сообщество",
                "cover_image_url": "https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?auto=format&fit=crop&w=800&q=80",
                "description": "Главный марафон страны с маршрутом по историческому центру Москвы: набережные, Садовое кольцо, Большой театр и Кремль."
            },
            {
                "title": "Golden Ring Ultra Trail (GRUT) 2026",
                "discipline": "трейл",
                "start_date": date(2026, 7, 18),
                "end_date": date(2026, 7, 19),
                "city": "Суздаль",
                "region": "Владимирская область",
                "country": "Россия",
                "latitude": 56.4172,
                "longitude": 40.4489,
                "distances": ["T10", "T20", "T30", "T50", "T80", "T100 (108 км)"],
                "elevation_gain_m": 450,
                "registration_status": "closing_soon",
                "registration_link": "https://goldenringtrail.ru/",
                "official_website": "https://runningheroes.ru/",
                "min_price": 4000.0,
                "max_price": 11000.0,
                "organizer": "Running Heroes Russia",
                "cover_image_url": "https://images.unsplash.com/photo-1502680390469-be75c86b636f?auto=format&fit=crop&w=800&q=80",
                "description": "Крупнейший трейловый фестиваль России в древнем Суздале. Броды, заливные луга, вековые леса и незабываемая атмосфера праздника."
            },
            {
                "title": "IRONSTAR SIRIUS SOCHI 2026",
                "discipline": "триатлон",
                "start_date": date(2026, 10, 10),
                "end_date": date(2026, 10, 11),
                "city": "Сочи / Сириус",
                "region": "Краснодарский край",
                "country": "Россия",
                "latitude": 43.4034,
                "longitude": 39.9553,
                "distances": ["113 (1.9 км плавание + 90 км вело + 21.1 км бег)", "226 (Ironman дистанция)", "Olympic", "Swimstar"],
                "elevation_gain_m": 850,
                "registration_status": "open",
                "registration_link": "https://iron-star.com/event/ironstar-sirius-sochi-2026/",
                "official_website": "https://iron-star.com/",
                "min_price": 12000.0,
                "max_price": 32000.0,
                "organizer": "IRONSTAR",
                "cover_image_url": "https://images.unsplash.com/photo-1530549387789-4c1017266635?auto=format&fit=crop&w=800&q=80",
                "description": "Финал сезона триатлона на побережье Черного моря. Заплыв в защищенной бухте Имеретинского порта и скоростной велоэтап по трассе Формулы-1 и шоссе на Красную Поляну."
            },
            {
                "title": "Полумарафон «Бегом по Золотому кольцу» — Ярославль",
                "discipline": "бег",
                "start_date": date(2026, 9, 6),
                "end_date": date(2026, 9, 6),
                "city": "Ярославль",
                "region": "Ярославская область",
                "country": "Россия",
                "latitude": 57.6261,
                "longitude": 39.8845,
                "distances": ["3 км", "10 км", "21.1 км"],
                "elevation_gain_m": 80,
                "registration_status": "open",
                "registration_link": "https://goldenringrun.ru/yaroslavl",
                "official_website": "https://goldenringrun.ru/",
                "min_price": 2000.0,
                "max_price": 3800.0,
                "organizer": "Бегом по Золотому кольцу",
                "cover_image_url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80",
                "description": "Флагманский старт серии «Фармэко — Бегом по Золотому кольцу». Старт на знаменитой Волжской стрелке у слияния рек Волги и Которосли."
            },
            {
                "title": "Гонка Героев — Алабино (Открытие Сезона)",
                "discipline": "гонки_с_препятствиями",
                "start_date": date(2026, 5, 23),
                "end_date": date(2026, 5, 23),
                "city": "Алабино",
                "region": "Московская область",
                "country": "Россия",
                "latitude": 55.5348,
                "longitude": 36.9691,
                "distances": ["10 км + 35 препятствий (Чемпионат)", "8 км (Массовый старт)"],
                "elevation_gain_m": 150,
                "registration_status": "open",
                "registration_link": "https://heroleague.ru/race",
                "official_website": "https://heroleague.ru/",
                "min_price": 3900.0,
                "max_price": 6000.0,
                "organizer": "Лига Героев",
                "cover_image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80",
                "description": "Экстремальный забег с препятствиями на полигоне: рукоходы, рвы с водой, колючая проволока, грязевые траншеи и легендарная стена «Эверест»."
            },
            {
                "title": "Казанский Марафон 2026",
                "discipline": "бег",
                "start_date": date(2026, 5, 10),
                "end_date": date(2026, 5, 11),
                "city": "Казань",
                "region": "Республика Татарстан",
                "country": "Россия",
                "latitude": 55.7961,
                "longitude": 49.1064,
                "distances": ["3 км", "10 км", "21.1 км", "42.2 км"],
                "elevation_gain_m": 110,
                "registration_status": "open",
                "registration_link": "https://kazanmarathon.org/",
                "official_website": "https://timerman.org/",
                "min_price": 2200.0,
                "max_price": 4500.0,
                "organizer": "TIMERMAN",
                "cover_image_url": "https://images.unsplash.com/photo-1530549387789-4c1017266635?auto=format&fit=crop&w=800&q=80",
                "description": "Один из красивейших и самых плоских марафонов Европы. Маршрут проходит мимо Казанского кремля, мечети Кул-Шариф и акватории реки Казанки."
            },
            {
                "title": "Gran Fondo Russia — Волоколамск (Moscow Raceway)",
                "discipline": "велоспорт",
                "start_date": date(2026, 6, 28),
                "end_date": date(2026, 6, 28),
                "city": "Волоколамск",
                "region": "Московская область",
                "country": "Россия",
                "latitude": 55.9984,
                "longitude": 36.2758,
                "distances": ["30 км (заезд)", "60 км (заезд/гонка)", "100 км (гонка Gran Fondo)"],
                "elevation_gain_m": 620,
                "registration_status": "announced",
                "registration_link": "https://www.granfondo.ru/",
                "official_website": "https://www.granfondo.ru/",
                "min_price": 3200.0,
                "max_price": 5500.0,
                "organizer": "Korsa Media",
                "cover_image_url": "https://images.unsplash.com/photo-1517649763962-0c623266ddc0?auto=format&fit=crop&w=800&q=80",
                "description": "Популярнейшая в России шоссейная велогонка на безопасных перекрытых дорогах со стартом на автодроме Moscow Raceway."
            },
            {
                "title": "Elbrus World Race 2026",
                "discipline": "трейл",
                "start_date": date(2026, 8, 1),
                "end_date": date(2026, 8, 2),
                "city": "пос. Терскол / Приэльбрусье",
                "region": "Кабардино-Балкарская Республика",
                "country": "Россия",
                "latitude": 43.2500,
                "longitude": 42.5100,
                "distances": ["Garabashi 10 км", "Cheget 24 км", "Kahiani 35 км", "Elbrus 8 км Vertical", "Race 46 км", "Ultra 135 км вокруг Эльбруса"],
                "elevation_gain_m": 7200,
                "registration_status": "open",
                "registration_link": "https://elbrusworldrace.com/",
                "official_website": "https://elbrusworldrace.com/",
                "min_price": 5000.0,
                "max_price": 16000.0,
                "organizer": "Running Heroes Russia",
                "cover_image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
                "description": "Суровый высокогорный трейл вокруг высочайшей вершины Европы — горы Эльбрус. Высоты до 3700 м над уровнем моря, ледники и перевалы."
            }
        ]

        return sample_events[:limit]

    def save_items(self, db: Session, items: List[Dict[str, Any]]) -> Dict[str, int]:
        added = 0
        updated = 0
        for item_data in items:
            existing = db.query(SportEvent).filter(
                SportEvent.title == item_data["title"],
                SportEvent.start_date == item_data["start_date"]
            ).first()

            if existing:
                for k, v in item_data.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                event = SportEvent(**item_data)
                db.add(event)
                added += 1

        db.commit()
        return {"scanned": len(items), "added": added, "updated": updated}
