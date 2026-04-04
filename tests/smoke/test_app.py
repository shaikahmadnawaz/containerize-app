from fastapi.testclient import TestClient
import psycopg

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready_endpoint_missing_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    response = client.get("/ready")
    assert response.status_code == 503


def test_ready_endpoint_with_database_url(monkeypatch):
    class DummyCursor:
        def execute(self, query):
            assert query == "SELECT 1"

        def fetchone(self):
            return (1,)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class DummyConnection:
        def cursor(self):
            return DummyCursor()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setenv("DATABASE_URL", "postgresql://appuser:apppass@db:5432/appdb")
    monkeypatch.setattr("app.main.psycopg.connect", lambda *args, **kwargs: DummyConnection())
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_ready_endpoint_when_database_connection_fails(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://appuser:apppass@db:5432/appdb")

    def raise_operational_error(*args, **kwargs):
        raise psycopg.OperationalError("db unavailable")

    monkeypatch.setattr("app.main.psycopg.connect", raise_operational_error)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "database not ready"


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_info_endpoint_has_expected_fields():
    response = client.get("/info")
    assert response.status_code == 200
    payload = response.json()
    for field in ["hostname", "python_version", "os", "uptime_seconds", "environment"]:
        assert field in payload
