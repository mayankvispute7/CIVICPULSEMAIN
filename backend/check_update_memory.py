import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.learning_service import LearningService
from app.models.domain import Site

db = SessionLocal()
service = LearningService(db)
site = db.query(Site).first()
if site:
    try:
        mem = service.update_site_memory(site.site_id)
        print("Success")
    except Exception as e:
        import traceback
        traceback.print_exc()
else:
    print("No site")
