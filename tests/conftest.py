import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activity():
    """Provide sample activity data for testing"""
    return {
        "description": "Test Activity",
        "schedule": "Mondays, 3:00 PM - 4:00 PM",
        "max_participants": 5,
        "participants": []
    }
