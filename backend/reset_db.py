import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine, Base
from app.models.domain import Complaint, FailureCluster, FailureCase, Evidence, HistoricalIncident, Site, FailureHypothesis

def reset_db():
    print("Resetting database...")
    try:
        # Drop and recreate all tables to avoid FK issues
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("Database cleared successfully! You now have 0 complaints and 0 clusters.")
    except Exception as e:
        print(f"Error clearing database: {e}")

if __name__ == "__main__":
    reset_db()
