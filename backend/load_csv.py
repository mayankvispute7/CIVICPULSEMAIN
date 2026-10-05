import sys
import os
import csv
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.domain import Complaint

def load_csv(filepath):
    db = SessionLocal()
    count = 0
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            c = Complaint(
                complaint_id=row['complaint_id'],
                title=f"{row['category']} - {row['location']}",
                reported_at=datetime.strptime(row['reported_at'], '%Y-%m-%d %H:%M:%S'),
                description=row['complaint_text'],
                address=row['location'],
                ward=row['ward'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                category=row['category'],
                severity=row['severity'].upper(),
                status='OPEN',
                data_truth='SYNTHETIC_DATA'
            )
            db.add(c)
            count += 1
    db.commit()
    print(f"Loaded {count} complaints from {filepath}")
    db.close()

if __name__ == "__main__":
    load_csv("../pune_baner_complaints_20.csv")
