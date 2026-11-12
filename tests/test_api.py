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

def test_apparel_listing(client):
    response = client.get("/api/v1/apparel")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] > 0
    first = data["items"][0]
    assert "title" in first
    assert "brand" in first
    assert "price" in first
    assert "technologies" in first

def test_apparel_filter_by_brand(client):
    response = client.get("/api/v1/apparel?brand=Salomon")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert "Salomon" in item["brand"]

def test_apparel_filter_by_purpose(client):
    response = client.get("/api/v1/apparel?purpose=трейл")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

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

def test_parser_job_trigger_and_list(client):
    response = client.post("/api/v1/parsers/run", json={"domain": "events", "limit_per_source": 5})
    assert response.status_code == 200
    job = response.json()
    assert job["domain"] == "events"
    assert job["status"] in ("completed", "running")

    # Check jobs list
    jobs_resp = client.get("/api/v1/parsers/jobs")
    assert jobs_resp.status_code == 200
    jobs_data = jobs_resp.json()
    assert jobs_data["total"] >= 1
