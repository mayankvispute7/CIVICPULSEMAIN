import requests
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.database import SessionLocal
from app.models.domain import WorkOrder
db = SessionLocal()
wo = db.query(WorkOrder).first()
wo_id = wo.work_order_id
task_id = wo.tasks[0].task_id

ev_bad = {
    "work_order_id": wo_id,
    "task_id": task_id,
    "latitude": 19.112,
    "longitude": -72.100,
    "captured_at": datetime.now().isoformat() + "Z",
    "image_url": "http://example.com/bad.jpg",
    "metadata_info": {}
}
r_bad = requests.post(f"{BASE_URL}/execution/evidence", json=ev_bad)
print(r_bad.status_code)
print(r_bad.text)
