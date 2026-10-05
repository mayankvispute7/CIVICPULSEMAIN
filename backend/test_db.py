from app.db.database import SessionLocal
from app.models.domain import Complaint, FailureCluster, FailureCase, WorkOrder
db = SessionLocal()
print("Complaints:", db.query(Complaint).count())
print("Clusters:", db.query(FailureCluster).count())
print("Cases:", db.query(FailureCase).count())
print("WorkOrders:", db.query(WorkOrder).count())
