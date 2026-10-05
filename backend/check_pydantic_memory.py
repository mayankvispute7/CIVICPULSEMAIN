import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.domain import InfrastructureMemory
from app.schemas.api_schemas import InfrastructureMemoryResponse

db = SessionLocal()
mem = db.query(InfrastructureMemory).first()
if mem:
    try:
        resp = InfrastructureMemoryResponse.model_validate(mem)
        print("Success:", resp)
    except Exception as e:
        print("VALIDATION ERROR:")
        print(e)
else:
    print("No memory")
