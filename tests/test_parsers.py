import pytest
from datetime import date
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.apparel import ApparelProduct
from app.models.supplement import SupplementProduct
from app.models.event import SportEvent
from app.models.parser_job import ParserJob
from app.parsers.base import BaseParser, DEFAULT_HEADERS
from app.parsers.apparel_parser import ApparelCatalogParser
from app.parsers.supplement_parser import SupplementCatalogParser
from app.parsers.events_parser import EventsAggregatorParser
from app.parsers.runner import run_parser_job
import app.parsers as parsers_module


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def db_session():
    """Provides an isolated in-memory SQLite database session for each test."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


# ============================================================================
# 1. BaseParser Tests
# ============================================================================

class ConcreteParser(BaseParser):
    """Concrete implementation for testing abstract BaseParser."""
    async def parse(self, limit: int = 20):
        return [{"dummy": "item"}][:limit]

    def save_items(self, db, items):
        return {"scanned": len(items), "added": len(items), "updated": 0}


class TestBaseParser:
    def test_abstract_class_cannot_be_instantiated(self):
        """Verifies that BaseParser cannot be directly instantiated due to ABC."""
        with pytest.raises(TypeError) as exc_info:
            BaseParser("TestParser", "TestSource")
        assert "Can't instantiate abstract class BaseParser" in str(exc_info.value)

    def test_concrete_parser_initialization(self):
        """Checks attributes and client defaults when subclassing BaseParser."""
        parser = ConcreteParser(name="TestConcrete", source="TestMedia", timeout=10.0)
        assert parser.name == "TestConcrete"
        assert parser.source == "TestMedia"
        assert parser.timeout == 10.0
        assert isinstance(parser.client, httpx.AsyncClient)
        assert parser.client.headers.get("user-agent") == DEFAULT_HEADERS["User-Agent"]
        assert parser.client.headers.get("accept-language") == DEFAULT_HEADERS["Accept-Language"]

    @pytest.mark.anyio
    async def test_fetch_html_success(self):
        """Tests successful HTML content retrieval."""
        parser = ConcreteParser(name="TestFetch", source="Test")
        fake_html = "<html><body><h1>Sport Catalog</h1></body></html>"
        url = "https://example.com/catalog"
        req = httpx.Request("GET", url)
        mock_response = httpx.Response(200, text=fake_html, request=req)

        with patch.object(
            parser.client,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            html = await parser.fetch_html(url)
            assert html == fake_html
        await parser.close()

    @pytest.mark.anyio
    async def test_fetch_html_http_status_error(self):
        """Tests HTTP error handling during HTML fetch (e.g., 404 / 500)."""
        parser = ConcreteParser(name="TestFetch", source="Test")
        req = httpx.Request("GET", "https://example.com/not-found")
        mock_response = httpx.Response(404, request=req)

        with patch.object(
            parser.client,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await parser.fetch_html("https://example.com/not-found")
        await parser.close()

    @pytest.mark.anyio
    async def test_fetch_html_connection_exception(self):
        """Tests network/connection failure handling."""
        parser = ConcreteParser(name="TestFetch", source="Test")
        with patch.object(
            parser.client,
            "get",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("Network unreachable")
        ):
            with pytest.raises(httpx.ConnectError):
                await parser.fetch_html("https://example.com/broken")
        await parser.close()

    @pytest.mark.anyio
    async def test_fetch_json_success(self):
        """Tests successful JSON API response retrieval."""
        parser = ConcreteParser(name="TestFetch", source="Test")
        fake_payload = {"count": 2, "items": [{"id": 1}, {"id": 2}]}
        url = "https://api.example.com/items"
        req = httpx.Request("GET", url)
        mock_response = httpx.Response(200, json=fake_payload, request=req)

        with patch.object(
            parser.client,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            data = await parser.fetch_json(url)
            assert data == fake_payload
            assert data["count"] == 2
        await parser.close()

    @pytest.mark.anyio
    async def test_fetch_json_http_status_error(self):
        """Tests HTTP 500 error raising in fetch_json."""
        parser = ConcreteParser(name="TestFetch", source="Test")
        req = httpx.Request("GET", "https://api.example.com/error")
        mock_response = httpx.Response(500, request=req)

        with patch.object(
            parser.client,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await parser.fetch_json("https://api.example.com/error")
        await parser.close()

    @pytest.mark.anyio
    async def test_fetch_json_request_exception(self):
        """Tests general request error in fetch_json."""
        parser = ConcreteParser(name="TestFetch", source="Test")
        with patch.object(
            parser.client,
            "get",
            new_callable=AsyncMock,
            side_effect=httpx.ReadTimeout("Read timed out")
        ):
            with pytest.raises(httpx.ReadTimeout):
                await parser.fetch_json("https://api.example.com/timeout")
        await parser.close()

    @pytest.mark.anyio
    async def test_close_client(self):
        """Tests that close() invokes client.aclose()."""
        parser = ConcreteParser(name="TestClose", source="Test")
        with patch.object(parser.client, "aclose", new_callable=AsyncMock) as mock_aclose:
            await parser.close()
            mock_aclose.assert_awaited_once()


# ============================================================================
# 2. ApparelCatalogParser Tests
# ============================================================================

class TestApparelCatalogParser:
    def test_initialization(self):
        """Verifies default name and source."""
        parser = ApparelCatalogParser()
        assert parser.name == "ApparelCatalogParser"
        assert parser.source == "MultiSport Retail"

    @pytest.mark.anyio
    async def test_parse_limit_variations(self):
        """Tests parse with default, bounded, zero, and out-of-range limits."""
        parser = ApparelCatalogParser()
        try:
            items_default = await parser.parse()
            assert len(items_default) > 0
            assert len(items_default) <= 20

            items_2 = await parser.parse(limit=2)
            assert len(items_2) == 2

            items_0 = await parser.parse(limit=0)
            assert len(items_0) == 0

            items_large = await parser.parse(limit=100)
            assert len(items_large) == len(items_default)
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_parse_data_structure_validation(self):
        """Validates schema conformance and types of parsed apparel items."""
        parser = ApparelCatalogParser()
        try:
            items = await parser.parse(limit=5)
            assert len(items) >= 1

            required_fields = [
                "title", "brand", "model_name", "category", "subcategory",
                "gender", "purpose", "sizes", "price", "currency", "in_stock",
                "source", "source_url", "image_url", "technologies", "specs",
                "description", "rating", "reviews_count"
            ]

            for item in items:
                for field in required_fields:
                    assert field in item, f"Missing required field: {field}"
                assert isinstance(item["title"], str) and len(item["title"]) > 0
                assert isinstance(item["brand"], str)
                assert isinstance(item["price"], (int, float)) and item["price"] > 0
                assert isinstance(item["purpose"], list)
                assert isinstance(item["sizes"], list)
                assert isinstance(item["technologies"], list)
                assert isinstance(item["specs"], dict)
                assert isinstance(item["in_stock"], bool)
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_save_items_insert_new(self, db_session):
        """Tests saving newly parsed items into database."""
        parser = ApparelCatalogParser()
        try:
            items = await parser.parse(limit=3)
            result = parser.save_items(db_session, items)

            assert result["scanned"] == 3
            assert result["added"] == 3
            assert result["updated"] == 0

            # Verify in DB
            products = db_session.query(ApparelProduct).all()
            assert len(products) == 3

            first_prod = db_session.query(ApparelProduct).filter(
                ApparelProduct.title == items[0]["title"],
                ApparelProduct.brand == items[0]["brand"]
            ).first()
            assert first_prod is not None
            assert first_prod.model_name == items[0]["model_name"]
            assert first_prod.price == items[0]["price"]
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_save_items_update_existing(self, db_session):
        """Tests updating already existing products without duplicates."""
        parser = ApparelCatalogParser()
        try:
            items = await parser.parse(limit=2)
            parser.save_items(db_session, items)

            # Modify fields on existing items
            modified_items = [dict(item) for item in items]
            modified_items[0]["price"] = 9999.0
            modified_items[0]["rating"] = 5.0

            result = parser.save_items(db_session, modified_items)
            assert result["scanned"] == 2
            assert result["added"] == 0
            assert result["updated"] == 2

            # Check that count remains 2 and fields were updated
            total = db_session.query(ApparelProduct).count()
            assert total == 2

            updated_prod = db_session.query(ApparelProduct).filter(
                ApparelProduct.title == modified_items[0]["title"],
                ApparelProduct.brand == modified_items[0]["brand"]
            ).first()
            assert updated_prod.price == 9999.0
            assert updated_prod.rating == 5.0
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_save_items_mixed_insert_and_update(self, db_session):
        """Tests saving a batch containing both existing and brand new items."""
        parser = ApparelCatalogParser()
        try:
            items = await parser.parse(limit=2)
            # Save first item only
            parser.save_items(db_session, [items[0]])

            # Now save both: items[0] should update, items[1] should add
            result = parser.save_items(db_session, items)
            assert result["scanned"] == 2
            assert result["added"] == 1
            assert result["updated"] == 1

            assert db_session.query(ApparelProduct).count() == 2
        finally:
            await parser.close()

    def test_save_items_empty_list(self, db_session):
        """Tests that saving an empty list returns zeros and does not fail."""
        parser = ApparelCatalogParser()
        res = parser.save_items(db_session, [])
        assert res == {"scanned": 0, "added": 0, "updated": 0}


# ============================================================================
# 3. SupplementCatalogParser Tests
# ============================================================================

class TestSupplementCatalogParser:
    def test_initialization(self):
        """Verifies default name and source."""
        parser = SupplementCatalogParser()
        assert parser.name == "SupplementCatalogParser"
        assert parser.source == "Supplements & Nutrition Network"

    @pytest.mark.anyio
    async def test_parse_limit_variations(self):
        """Tests parse with varied limit arguments."""
        parser = SupplementCatalogParser()
        try:
            all_items = await parser.parse()
            assert len(all_items) > 0

            items_3 = await parser.parse(limit=3)
            assert len(items_3) == 3

            items_0 = await parser.parse(limit=0)
            assert len(items_0) == 0
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_parse_data_structure_validation(self):
        """Validates schema conformance of parsed supplements."""
        parser = SupplementCatalogParser()
        try:
            items = await parser.parse(limit=5)
            assert len(items) >= 1

            required_fields = [
                "title", "brand", "category", "form", "dosage",
                "serving_size", "servings_count", "composition",
                "target_goals", "flavors", "volume_weight", "price",
                "currency", "in_stock", "source", "source_url", "rating"
            ]

            for item in items:
                for field in required_fields:
                    assert field in item, f"Missing required supplement field: {field}"
                assert isinstance(item["title"], str)
                assert isinstance(item["brand"], str)
                assert isinstance(item["composition"], list)
                assert isinstance(item["target_goals"], list)
                assert isinstance(item["flavors"], list)
                assert isinstance(item["price"], (int, float)) and item["price"] > 0
                assert isinstance(item["servings_count"], int)
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_save_items_insert_new(self, db_session):
        """Tests inserting new supplement items into database."""
        parser = SupplementCatalogParser()
        try:
            items = await parser.parse(limit=3)
            res = parser.save_items(db_session, items)

            assert res["scanned"] == 3
            assert res["added"] == 3
            assert res["updated"] == 0

            db_items = db_session.query(SupplementProduct).all()
            assert len(db_items) == 3

            supp = db_session.query(SupplementProduct).filter(
                SupplementProduct.title == items[0]["title"],
                SupplementProduct.brand == items[0]["brand"]
            ).first()
            assert supp is not None
            assert supp.category == items[0]["category"]
            assert supp.form == items[0]["form"]
            assert supp.target_goals == items[0]["target_goals"]
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_save_items_update_existing(self, db_session):
        """Tests updating existing supplement products by title and brand."""
        parser = SupplementCatalogParser()
        try:
            items = await parser.parse(limit=2)
            parser.save_items(db_session, items)

            modified = [dict(i) for i in items]
            modified[0]["price"] = 1234.0
            modified[0]["dosage"] = "Новая дозировка 1000мг"

            res = parser.save_items(db_session, modified)
            assert res["scanned"] == 2
            assert res["added"] == 0
            assert res["updated"] == 2

            supp = db_session.query(SupplementProduct).filter(
                SupplementProduct.title == modified[0]["title"],
                SupplementProduct.brand == modified[0]["brand"]
            ).first()
            assert supp.price == 1234.0
            assert supp.dosage == "Новая дозировка 1000мг"
        finally:
            await parser.close()

    def test_save_items_empty_list(self, db_session):
        """Tests saving an empty list returns 0 for all metrics."""
        parser = SupplementCatalogParser()
        res = parser.save_items(db_session, [])
        assert res == {"scanned": 0, "added": 0, "updated": 0}


# ============================================================================
# 4. EventsAggregatorParser Tests
# ============================================================================

class TestEventsAggregatorParser:
    def test_initialization(self):
        """Verifies default name and source."""
        parser = EventsAggregatorParser()
        assert parser.name == "EventsAggregatorParser"
        assert parser.source == "Russia Sports Events Network"

    @pytest.mark.anyio
    async def test_parse_limit_variations(self):
        """Tests parse with different limit parameters."""
        parser = EventsAggregatorParser()
        try:
            all_events = await parser.parse()
            assert len(all_events) > 0

            events_2 = await parser.parse(limit=2)
            assert len(events_2) == 2

            events_0 = await parser.parse(limit=0)
            assert len(events_0) == 0
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_parse_data_structure_validation(self):
        """Validates schema conformance and types of parsed sports events."""
        parser = EventsAggregatorParser()
        try:
            events = await parser.parse(limit=5)
            assert len(events) >= 1

            required_fields = [
                "title", "discipline", "start_date", "end_date", "city",
                "region", "country", "latitude", "longitude", "distances",
                "elevation_gain_m", "registration_status", "registration_link",
                "official_website", "min_price", "organizer", "description"
            ]

            for event in events:
                for field in required_fields:
                    assert field in event, f"Missing required event field: {field}"
                assert isinstance(event["title"], str)
                assert isinstance(event["discipline"], str)
                assert isinstance(event["start_date"], date)
                assert isinstance(event["city"], str)
                assert isinstance(event["latitude"], float)
                assert isinstance(event["longitude"], float)
                assert isinstance(event["distances"], list)
                assert event["registration_status"] in ("open", "closing_soon", "sold_out", "announced")
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_save_items_insert_new(self, db_session):
        """Tests saving newly parsed events into database."""
        parser = EventsAggregatorParser()
        try:
            items = await parser.parse(limit=3)
            res = parser.save_items(db_session, items)

            assert res["scanned"] == 3
            assert res["added"] == 3
            assert res["updated"] == 0

            db_events = db_session.query(SportEvent).all()
            assert len(db_events) == 3

            first_event = db_session.query(SportEvent).filter(
                SportEvent.title == items[0]["title"],
                SportEvent.start_date == items[0]["start_date"]
            ).first()
            assert first_event is not None
            assert first_event.city == items[0]["city"]
            assert first_event.discipline == items[0]["discipline"]
            assert first_event.registration_link == items[0]["registration_link"]
        finally:
            await parser.close()

    @pytest.mark.anyio
    async def test_save_items_update_existing(self, db_session):
        """Tests updating existing events by (title, start_date)."""
        parser = EventsAggregatorParser()
        try:
            items = await parser.parse(limit=2)
            parser.save_items(db_session, items)

            modified = [dict(i) for i in items]
            modified[0]["registration_status"] = "sold_out"
            modified[0]["min_price"] = 5500.0

            res = parser.save_items(db_session, modified)
            assert res["scanned"] == 2
            assert res["added"] == 0
            assert res["updated"] == 2

            ev = db_session.query(SportEvent).filter(
                SportEvent.title == modified[0]["title"],
                SportEvent.start_date == modified[0]["start_date"]
            ).first()
            assert ev.registration_status == "sold_out"
            assert ev.min_price == 5500.0
        finally:
            await parser.close()

    def test_save_items_empty_list(self, db_session):
        """Tests that saving an empty list returns zeros."""
        parser = EventsAggregatorParser()
        res = parser.save_items(db_session, [])
        assert res == {"scanned": 0, "added": 0, "updated": 0}


# ============================================================================
# 5. Parser Runner (run_parser_job) Tests
# ============================================================================

class TestParserRunner:
    @pytest.mark.anyio
    async def test_run_parser_job_apparel_only(self, db_session):
        """Tests execution of parser job restricted to 'apparel' domain."""
        job = await run_parser_job(db=db_session, domain="apparel", limit=4)

        assert job.status == "completed"
        assert job.domain == "apparel"
        assert job.items_scanned == 4
        assert job.items_added == 4
        assert job.items_updated == 0
        assert job.errors_count == 0
        assert job.error_message is None
        assert job.started_at is not None
        assert job.completed_at is not None
        assert job.job_id.startswith("job-")

        # Verify only apparel records exist
        assert db_session.query(ApparelProduct).count() == 4
        assert db_session.query(SupplementProduct).count() == 0
        assert db_session.query(SportEvent).count() == 0

        # Verify job is saved in parser_jobs table
        saved_job = db_session.query(ParserJob).filter(ParserJob.job_id == job.job_id).first()
        assert saved_job is not None
        assert saved_job.status == "completed"

    @pytest.mark.anyio
    async def test_run_parser_job_supplements_only(self, db_session):
        """Tests execution of parser job for 'supplements' domain."""
        job = await run_parser_job(db=db_session, domain="supplements", limit=3)

        assert job.status == "completed"
        assert job.domain == "supplements"
        assert job.items_scanned == 3
        assert job.items_added == 3
        assert job.errors_count == 0

        assert db_session.query(SupplementProduct).count() == 3
        assert db_session.query(ApparelProduct).count() == 0
        assert db_session.query(SportEvent).count() == 0

    @pytest.mark.anyio
    async def test_run_parser_job_events_only(self, db_session):
        """Tests execution of parser job for 'events' domain."""
        job = await run_parser_job(db=db_session, domain="events", limit=5)

        assert job.status == "completed"
        assert job.domain == "events"
        assert job.items_scanned == 5
        assert job.items_added == 5
        assert job.errors_count == 0

        assert db_session.query(SportEvent).count() == 5
        assert db_session.query(ApparelProduct).count() == 0
        assert db_session.query(SupplementProduct).count() == 0

    @pytest.mark.anyio
    async def test_run_parser_job_all_domains(self, db_session):
        """Tests executing multi-domain parser job ('all')."""
        limit = 2
        job = await run_parser_job(db=db_session, domain="all", limit=limit)

        assert job.status == "completed"
        assert job.domain == "all"
        assert job.items_scanned == limit * 3
        assert job.items_added == limit * 3
        assert job.items_updated == 0
        assert job.errors_count == 0

        assert db_session.query(ApparelProduct).count() == limit
        assert db_session.query(SupplementProduct).count() == limit
        assert db_session.query(SportEvent).count() == limit

    @pytest.mark.anyio
    async def test_run_parser_job_idempotent_re_run(self, db_session):
        """Tests that running the job a second time updates existing records instead of duplicating."""
        job1 = await run_parser_job(db=db_session, domain="apparel", limit=3)
        assert job1.items_added == 3
        assert job1.items_updated == 0

        job2 = await run_parser_job(db=db_session, domain="apparel", limit=3)
        assert job2.status == "completed"
        assert job2.items_scanned == 3
        assert job2.items_added == 0
        assert job2.items_updated == 3

        # Count in DB remains 3
        assert db_session.query(ApparelProduct).count() == 3

    @pytest.mark.anyio
    async def test_run_parser_job_failure_handling(self, db_session):
        """Tests graceful failure handling when a parser raises an unhandled exception."""
        with patch.object(
            ApparelCatalogParser,
            "parse",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Scraper connection timeout or banned IP")
        ):
            job = await run_parser_job(db=db_session, domain="apparel", limit=5)

            assert job.status == "failed"
            assert job.errors_count == 1
            assert "Scraper connection timeout or banned IP" in job.error_message
            assert job.completed_at is not None

            # Verify in DB
            db_job = db_session.query(ParserJob).filter(ParserJob.job_id == job.job_id).first()
            assert db_job.status == "failed"
            assert db_job.errors_count == 1

    @pytest.mark.anyio
    async def test_run_parser_job_closes_parser_on_failure(self, db_session):
        """Verifies that parser.close() is called even if an exception occurs during parsing."""
        close_called = False

        original_close = ApparelCatalogParser.close
        async def fake_close(self):
            nonlocal close_called
            close_called = True
            await original_close(self)

        with patch.object(ApparelCatalogParser, "close", fake_close):
            with patch.object(
                ApparelCatalogParser,
                "parse",
                new_callable=AsyncMock,
                side_effect=ValueError("Parse failed")
            ):
                await run_parser_job(db=db_session, domain="apparel")
                assert close_called is True

    @pytest.mark.anyio
    async def test_run_parser_job_unrecognized_domain(self, db_session):
        """Tests running with a domain not handled by runner branches."""
        job = await run_parser_job(db=db_session, domain="unknown_domain", limit=10)
        assert job.status == "completed"
        assert job.items_scanned == 0
        assert job.items_added == 0
        assert job.items_updated == 0


# ============================================================================
# 6. Module Exports Test
# ============================================================================

def test_parsers_module_all_exports():
    """Ensures app.parsers exports all expected classes and functions."""
    expected = [
        "BaseParser",
        "ApparelCatalogParser",
        "SupplementCatalogParser",
        "EventsAggregatorParser",
        "run_parser_job",
    ]
    for name in expected:
        assert hasattr(parsers_module, name)
        assert name in parsers_module.__all__
