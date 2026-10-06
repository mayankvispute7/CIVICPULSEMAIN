import os, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.outcome_service import OutcomeService
from datetime import datetime

engine = create_engine('sqlite:///backend/app/civicpulse.db')
Session = sessionmaker(bind=engine)
db = Session()

service = OutcomeService(db)
try:
  service.record_outcome(
    case_id='f271b76e-5a73-402a-b237-2718c352bf8f',
    observed_at=datetime.now(),
    status='IMPROVED',
    trigger_event='test',
    work_order_id='test'
  )
except Exception as e:
  import traceback
  traceback.print_exc()

