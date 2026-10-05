import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.domain import FieldEvidence

db = SessionLocal()
ev = db.query(FieldEvidence).first()
if ev:
    print(f"metadata_info: {ev.metadata_info} (type: {type(ev.metadata_info)})")
    print(f"manipulation_indicators: {ev.manipulation_indicators} (type: {type(ev.manipulation_indicators)})")
else:
    print("No evidence found")
