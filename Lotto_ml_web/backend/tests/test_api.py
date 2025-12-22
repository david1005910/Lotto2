import pytest
from fastapi.testclient import TestClient

from main import app
from models.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Initialize database before each test."""
    init_db()


class TestRootEndpoints:
    """Test root and health endpoints."""

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestResultsEndpoints:
    """Test results API endpoints."""

    def test_get_results_empty(self):
        response = client.get("/api/v1/results")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "results" in data["data"]
        assert "pagination" in data["data"]

    def test_get_results_with_pagination(self):
        response = client.get("/api/v1/results?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 10

    def test_get_result_not_found(self):
        response = client.get("/api/v1/results/9999")
        assert response.status_code == 404


class TestStatisticsEndpoints:
    """Test statistics API endpoints."""

    def test_get_statistics(self):
        response = client.get("/api/v1/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "number_frequency" in data["data"]
        assert "odd_even_distribution" in data["data"]

    def test_get_statistics_with_recent(self):
        response = client.get("/api/v1/statistics?recent=100")
        assert response.status_code == 200


class TestRecommendEndpoints:
    """Test recommend API endpoints."""

    def test_get_recommendations(self):
        response = client.get("/api/v1/recommend")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestAdminEndpoints:
    """Test admin API endpoints."""

    def test_get_status(self):
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "database" in data["data"]
        assert "ml_models" in data["data"]


class TestPredictEndpoints:
    """Test predict API endpoints."""

    def test_predict_endpoint(self):
        response = client.get("/api/v1/predict")
        # If models exist, should return 200 with predictions
        # If models don't exist, should return 400
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert "predictions" in data["data"]
            assert "disclaimer" in data["data"]
        else:
            assert response.status_code == 400
