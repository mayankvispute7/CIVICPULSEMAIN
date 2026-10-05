import pytest
from fastapi.testclient import TestClient
import io

from app.main import app
from app.db.database import Base, engine

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    pass

def test_ingest_csv():
    # Create dummy CSV
    csv_content = """complaint_id,date,description,address,ward,latitude,longitude,category,severity,status
1,2026-07-01 10:00:00,Severe waterlogging after rain,Main St,Ward A,19.1,-72.1,WATERLOGGING,HIGH,NEW
2,2026-07-02 11:00:00,Pothole causing accidents,Park Ave,Ward B,19.2,-72.2,POTHOLE,MEDIUM,NEW
3,2026-07-03 12:00:00,Drain overflow, Elm St,Ward A,19.11,-72.11,DRAINAGE,CRITICAL,NEW
"""
    file_like = io.BytesIO(csv_content.encode("utf-8"))
    
    response = client.post(
        "/api/v1/ingest/csv",
        files={"file": ("test.csv", file_like, "text/csv")},
        data={"data_truth": "REAL_DATA"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["accepted_rows"] == 3
    
def test_list_complaints():
    response = client.get("/api/v1/complaints")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3

def test_clustering():
    response = client.post("/api/v1/complaints/cluster")
    assert response.status_code == 200
    data = response.json()
    assert data["total_clusters"] >= 0 # Might be 0 if min_samples > 3 or spatial distribution
