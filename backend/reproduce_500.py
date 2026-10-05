import sys
import os

# Add backend to sys path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.execution_service import ExecutionService
import traceback

db = SessionLocal()
service = ExecutionService(db)

# Find the task that we tried to delay
from app.models.domain import WorkOrderTask
tasks = db.query(WorkOrderTask).all()
if tasks:
    task_id = tasks[0].task_id
    print(f"Delaying task {task_id}")
    try:
        service.delay_task(task_id, "Rain delay", 24.0)
        print("Success")
    except Exception as e:
        print("EXCEPTION CAUGHT:")
        traceback.print_exc()
else:
    print("No tasks found")
