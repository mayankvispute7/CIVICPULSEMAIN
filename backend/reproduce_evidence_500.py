import sys
import os
import requests
from datetime import datetime

# Add backend to sys path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.verification_service import VerificationService
import traceback

db = SessionLocal()
service = VerificationService(db)

# Find the work order
from app.models.domain import WorkOrder
wos = db.query(WorkOrder).all()
if wos:
    wo_id = wos[0].work_order_id
    task_id = wos[0].tasks[0].task_id if wos[0].tasks else None
    print(f"Submit evidence for wo {wo_id}")
    try:
        service.submit_field_evidence(
            work_order_id=wo_id,
            latitude=19.112,
            longitude=-72.100,
            captured_at=datetime.utcnow(),
            task_id=task_id,
            image_url="http://example.com/bad.jpg",
            metadata_info={}
        )
        print("Success")
    except Exception as e:
        print("EXCEPTION CAUGHT:")
        traceback.print_exc()
else:
    print("No work orders found")
