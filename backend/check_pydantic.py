import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.domain import FieldEvidence
from app.schemas.api_schemas import FieldEvidenceResponse

db = SessionLocal()
ev = db.query(FieldEvidence).first()
if ev:
    try:
        resp = FieldEvidenceResponse.model_validate(ev)
        print("Success:", resp)
    except Exception as e:
        print("VALIDATION ERROR:")
        print(e)
else:
    print("No evidence")
