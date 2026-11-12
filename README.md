# Sport, Supplements & Events Hub API ⚡

Масштабируемый мультидоменный бэкенд, парсер и поисковая система, объединяющая:
1. **Каталог и датасет беговой экипировки (20 целевых категорий)** с жесткой таксономией брендов и схемой данных для модуля **AI Vision** (распознавание кроссовок и одежды по фото).
2. **Инфраструктура парсинга с ротацией IP и антифродом:** поддержка пулов прокси (Proxy6 / HTTP / SOCKS5), автоматическая подмена User-Agent и защитных заголовков (Client Hints).
3. **Очистка и нормализация (Sanitization):** сведение всех вариантов написания брендов (`ASICS`, `асикс` → `Asics`, `найк` → `Nike`) и категорий к каноническому формату без дубликатов.
4. **Фоновая автоматизация:** планировщик для регулярного обновления цен, размеров и новых коллекций по расписанию.
5. **Каталог спортивного питания и БАДов** с фильтрацией по целям (набор массы, сушка, выносливость, восстановление, суставы).
6. **Единый агрегатор спортивных событий РФ** (забеги, марафоны, трейлы, триатлон Ironstar, гонки с препятствиями «Лига Героев», велоспорт) с гео-фильтрацией по радиусу и регионам.
7. **Документированный REST API** (OpenAPI / Swagger) для интеграции с мобильными приложениями (**MaxFunFit**).
8. **Интерактивный веб-дашборд / тестбенч** для наглядного тестирования всех функций прямо в браузере.

---

## 🏷 20 Целевых категорий и брендовая таксономия (п. 3 ТЗ)

| № | Категория | Целевые бренды |
|---|---|---|
| 1 | **Носки** | Compressport, CEP, X-Bionic, Falke, Balega, Injinji, Nike, Asics |
| 2 | **Обувь** | Nike, Hoka, Salomon, Asics, Brooks, Saucony, New Balance, Puma, Adidas |
| 3 | **Гетры (Компрессия)** | CEP, Compressport, 2XU, X-Bionic, BV Sport, Nike, Salomon |
| 4 | **Нижнее белье / Спортивные бра** | Shock Absorber, Nike, Under Armour, Adidas, Reebok, 2XU, Odlo, Craft |
| 5 | **Шорты** | Nike, Adidas, Salomon, Asics, Puma, Under Armour, Brooks, New Balance, Craft |
| 6 | **Тайтсы** | 2XU, Nike, Asics, Salomon, Under Armour, Skins, Gore Wear, Craft |
| 7 | **Брюки** | Nike, Adidas, Puma, Asics, Salomon, The North Face, Under Armour |
| 8 | **Майки** | Nike, Asics, Salomon, Adidas, Puma, Saucony, Brooks, Under Armour, Ciele |
| 9 | **Футболки** | Nike, Asics, Salomon, Adidas, Under Armour, Puma, Brooks, Hoka, Craft |
| 10 | **Лонгсливы** | Nike, Asics, Salomon, Adidas, Under Armour, Gore Wear, Craft, The North Face |
| 11 | **Термобелье** | Craft, X-Bionic, Odlo, Brubeck, Icebreaker, The North Face, Salomon |
| 12 | **Кофты / Мидлееры** | Nike, Salomon, Asics, The North Face, Adidas, Under Armour, Columbia |
| 13 | **Жилеты** | Nike, Salomon, Asics, Gore Wear, Craft, The North Face, Adidas |
| 14 | **Ветровки** | Salomon, Nike, Asics, Gore Wear, The North Face, Dynafit, Adidas, Craft |
| 15 | **Куртки (Мембраны)** | Gore Wear, Salomon, The North Face, Nike, Dynafit, Arcteryx, Asics |
| 16 | **Перчатки** | Salomon, Nike, Asics, Craft, Gore Wear, The North Face, Under Armour |
| 17 | **Баффы (Гейтеры)** | Buff, Salomon, Nike, Asics, Craft, The North Face, Dynafit |
| 18 | **Кепки / Козырьки** | Compressport, Salomon, Nike, Buff, Asics, Ciele, Under Armour |
| 19 | **Повязки** | Buff, Salomon, Nike, Asics, Compressport, Craft, Under Armour |
| 20 | **Шапки** | Buff, Salomon, Asics, Nike, Craft, The North Face, Gore Wear |

---

## 📊 Структура собираемых данных (Схема БД, п. 2 ТЗ)

Для каждой единицы товара парсер собирает и нормализует следующий набор атрибутов:
- `sku_id` — Уникальный артикул товара на стороне источника.
- `category` — Строгое соответствие списку из 20 категорий.
- `brand` — Приведение к каноническому формату (Sanitizer).
- `product_name` — Полное наименование модели.
- `gender` — Мужской / Женский / Унисекс.
- `price_current` — Актуальная цена (руб.).
- `sizes` — Список доступных размеров (RU, EU, US, S/M/L/XL).
- `image_urls` — Массив ссылок на фото в высоком разрешении (датасет для AI Vision).
- `source_url` — Прямая ссылка на страницу товара.

---

## 🛡 Инфраструктура парсинга и обход антифрода (п. 4 ТЗ)

1. **Ротация IP (Proxy Pool):**
   - Встроенный менеджер прокси [`ProxyManager`](file:///c:/AG/01.%20Парсер/app/core/proxy_manager.py).
   - Поддержка пула прокси (Proxy6 / HTTP / SOCKS5) в формате `http://user:pass@ip:port`.
   - Задание списка через переменную окружения `PROXIES_LIST`, файл `proxies.txt` или API эндпоинт `POST /api/v1/parsers/proxies`.
   - Автоматическая ротация Round-Robin и отслеживание здоровья прокси с изоляцией сбойных узлов.

2. **Подмена заголовков (User-Agent Spoofing):**
   - Пул современных User-Agent (Chrome Windows/Mac, Safari iOS, Android Chrome, Edge).
   - Автоматическая генерация связанных заголовков: `Sec-Ch-Ua`, `Sec-Ch-Ua-Mobile`, `Sec-Ch-Ua-Platform`, `Accept-Language`, `Sec-Fetch-Dest`.

3. **Очистка (Sanitization Service):**
   - [`SanitizerService`](file:///c:/AG/01.%20Парсер/app/services/sanitizer.py) нормализует входящие названия брендов (исключая дубли вроде `ASICS`, `асикс` → `Asics`).
   - Сопоставление категорий по регулярным выражениям и ключевым словам.

4. **Фоновая автоматизация (Scheduler):**
   - Фоновый асинхронный планировщик [`ParserScheduler`](file:///c:/AG/01.%20Парсер/app/services/scheduler.py) запускает синхронизацию каждые N часов (настраивается параметром `PARSER_INTERVAL_HOURS`).
   - Управление расписанием через API: `GET /api/v1/parsers/scheduler` и `POST /api/v1/parsers/scheduler/toggle`.

---

## 🚀 Быстрый запуск

### Вариант 1. Локальный запуск (Python)

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Запуск сервера
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Веб-дашборд:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Вариант 2. Запуск в Docker с PostgreSQL + PostGIS

```bash
docker-compose up --build
```

---

## 🧪 Запуск полного набора тестов

```bash
python -m pytest -v
```
**Все 52 теста пройдены на 100%**, включая тесты таксономии 20 категорий, санитайзера брендов, пула прокси, фонового планировщика и AI Vision.
