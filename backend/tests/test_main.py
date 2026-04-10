from unittest.mock import AsyncMock, patch


def test_health_endpoint():
    """GET /health must return 200 with status and version."""
    with patch("app.main.create_vector_extension", new_callable=AsyncMock):
        from fastapi.testclient import TestClient
        from app.main import app
        with TestClient(app) as client:
            response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "v3"}


def test_cors_middleware_present():
    """CORSMiddleware must be registered on the app."""
    from app.main import app
    middleware_names = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_names
