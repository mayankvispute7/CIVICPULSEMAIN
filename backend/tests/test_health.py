import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import Base, engine

client = TestClient(app)

def setup_module(module):
    # Ensure tables are created for tests
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
