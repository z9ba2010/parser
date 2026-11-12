import os
import sys
import io
import asyncio
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import engine, Base, SessionLocal
from app.db.seed_data import seed_initial_data_if_empty
from app.services.sanitizer import sanitizer, TAXONOMY_CATEGORIES, CANONICAL_CATEGORIES

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensure database schema is created and seeded before running tests."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        asyncio.run(seed_initial_data_if_empty(db))
    yield

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_apparel_listing_and_schema_fields(client):
    """Verify that all required fields from Section 2 of ТЗ are present."""
    response = client.get("/api/v1/apparel")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 20

    first = data["items"][0]
    # Check strict fields from section 2 of ТЗ
    assert "sku_id" in first
    assert "category" in first
    assert "brand" in first
    assert "product_name" in first
    assert "gender" in first
    assert "price_current" in first
    assert "sizes" in first
    assert "image_urls" in first
    assert "source_url" in first
    assert isinstance(first["image_urls"], list)

def test_apparel_taxonomy_endpoint(client):
    """Verify 20 categories taxonomy endpoint matches ТЗ requirements."""
    response = client.get("/api/v1/apparel/taxonomy")
    assert response.status_code == 200
    data = response.json()
    assert data["total_categories"] == 20
    assert "categories" in data
    
    # Check sample key categories and brands
    assert "Носки" in data["categories"]
    assert "Compressport" in data["categories"]["Носки"]
    assert "Обувь" in data["categories"]
    assert "Hoka" in data["categories"]["Обувь"]
    assert "Куртки (Мембраны)" in data["categories"]
    assert "Arcteryx" in data["categories"]["Куртки (Мембраны)"]

def test_sanitization_brand_normalization():
    """Verify brand normalization rules (ASICS, асикс -> Asics, etc.)."""
    assert sanitizer.normalize_brand("ASICS") == "Asics"
    assert sanitizer.normalize_brand("асикс") == "Asics"
    assert sanitizer.normalize_brand("hoka one one") == "Hoka"
    assert sanitizer.normalize_brand("ХОКА") == "Hoka"
    assert sanitizer.normalize_brand("найк") == "Nike"
    assert sanitizer.normalize_brand("NIKE running") == "Nike"
    assert sanitizer.normalize_brand("the north face") == "The North Face"
    assert sanitizer.normalize_brand("tnf") == "The North Face"
    assert sanitizer.normalize_brand("2xu") == "2XU"
    assert sanitizer.normalize_brand("x-bionic") == "X-Bionic"
    assert sanitizer.normalize_brand("Gore-Wear") == "Gore Wear"

def test_sanitization_category_normalization():
    """Verify category normalization maps to exact 20 target categories."""
    assert sanitizer.normalize_category("socks", "беговые носки") == "Носки"
    assert sanitizer.normalize_category("calves", "компрессионные гетры для бега") == "Гетры (Компрессия)"
    assert sanitizer.normalize_category("tights", "зимние тайтсы") == "Тайтсы"
    assert sanitizer.normalize_category("jacket", "мембранная куртка gore-tex") == "Куртки (Мембраны)"
    assert sanitizer.normalize_category("windbreaker", "легкая ветровка") == "Ветровки"
    assert sanitizer.normalize_category("beanie", "теплая шапка") == "Шапки"
    assert sanitizer.normalize_category("buff", "беговой бафф гейтер") == "Баффы (Гейтеры)"

def test_apparel_filter_by_brand(client):
    response = client.get("/api/v1/apparel?brand=Salomon")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert "Salomon" in item["brand"]

def test_apparel_filter_by_category(client):
    response = client.get("/api/v1/apparel?category=Обувь")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["category"] == "Обувь"

def test_supplements_listing(client):
    response = client.get("/api/v1/supplements")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] > 0
    first = data["items"][0]
    assert "category" in first
    assert "form" in first
    assert "target_goals" in first

def test_supplements_filter_by_goal(client):
    response = client.get("/api/v1/supplements?target_goal=выносливость")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

def test_events_listing(client):
    response = client.get("/api/v1/events")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] > 0
    first = data["items"][0]
    assert "discipline" in first
    assert "city" in first
    assert "registration_link" in first

def test_events_geo_radius(client):
    # Moscow coordinates: 55.7558, 37.6173
    response = client.get("/api/v1/events?lat=55.7558&lon=37.6173&radius_km=200")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["distance_km"] is not None
        assert item["distance_km"] <= 200.0

def test_vision_recognition_file_upload(client):
    """Test mobile camera image file upload to visual recognition endpoint."""
    fake_image_bytes = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    files = {"file": ("nike_pegasus_shoe.jpg", io.BytesIO(fake_image_bytes), "image/jpeg")}
    response = client.post("/api/v1/vision/recognize", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "detected" in data
    assert "recognition_engine" in data
    assert data["detected"]["brand"] is not None
    assert data["matched_product"] is not None
    assert data["matched_product"]["brand"] is not None
    assert data["matched_product"]["sku_id"] is not None

def test_proxy_manager_and_endpoints(client):
    """Verify proxy management infrastructure."""
    response = client.get("/api/v1/parsers/proxies")
    assert response.status_code == 200
    data = response.json()
    assert "total_proxies" in data
    assert "healthy_proxies" in data

    # Add proxy
    add_resp = client.post("/api/v1/parsers/proxies", json={"proxy_url": "http://user:pass@194.67.1.1:8000"})
    assert add_resp.status_code == 200
    assert add_resp.json()["total_proxies"] >= 1

def test_scheduler_status(client):
    """Verify scheduler status endpoint."""
    response = client.get("/api/v1/parsers/scheduler")
    assert response.status_code == 200
    data = response.json()
    assert "is_running" in data
    assert "interval_hours" in data

def test_parser_job_trigger_with_category(client):
    """Trigger parser with specific category."""
    response = client.post("/api/v1/parsers/run", json={"domain": "apparel", "category": "Носки", "limit_per_source": 10})
    assert response.status_code == 200
    job = response.json()
    assert "apparel" in job["domain"]
    assert job["status"] in ("completed", "running")
