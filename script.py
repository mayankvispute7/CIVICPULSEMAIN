import sys
sys.path.append('backend')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///backend/app/civicpulse.db')
Session = sessionmaker(bind=engine)
session = Session()
from app.services.learning_service import LearningService
ls = LearningService(session)
ls.update_site_memory('bd5592e3-fea9-41d8-90af-c24ed327c855')
session.commit()
