import os
import sys
import logging
import json
from pprint import pprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.csv_ingestion_service import CSVIngestionService
from app.services.clustering_service import ClusteringService
from app.models.domain import Complaint, FailureCluster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    
    # 1. Ingest Data
    csv_path = "../pune_baner_complaints_20.csv"
    ingestion_service = CSVIngestionService(db)
    
    with open(csv_path, 'rb') as f:
        file_content = f.read()
        
    logger.info("Ingesting CSV...")
    import_result = ingestion_service.ingest_csv(
        filename="pune_baner_complaints_20.csv",
        content=file_content,
        data_truth="REAL_DATA"
    )
    
    logger.info(f"Ingested {import_result.accepted_rows} rows.")
    
    # 2. Run Clustering (Canonical)
    clustering_service = ClusteringService(db)
    logger.info("Running custom clustering algorithm...")
    cluster_result = clustering_service.run_clustering()
    
    complaints = db.query(Complaint).all()
    clusters = db.query(FailureCluster).all()
    
    logger.info(f"Total Clusters: {len(clusters)}")
    for c in clusters:
        logger.info(f"Cluster: {c.title}")
        logger.info(f"Complaints: {c.complaint_count}")
        logger.info(f"Incidents (Episodes): {c.incident_count}")
        logger.info(f"Confidence Level: {c.confidence_level}")
        logger.info(f"Relationship Evidence: {json.dumps(c.relationship_evidence, indent=2)}")
        logger.info(f"Rationale: {c.cluster_rationale}")
        logger.info("-" * 40)
        
    # Write Report
    with open("CLUSTERING_DIAGNOSTIC_REPORT.md", "w") as f:
        f.write("# CIVIC PULSE: CLUSTERING DIAGNOSTIC REPORT\n\n")
        f.write("## 1. Canonical Dataset Test\n")
        f.write(f"- **Total Complaints:** {len(complaints)}\n")
        f.write(f"- **Total Clusters:** {len(clusters)}\n")
        
        unclustered = len([c for c in complaints if not c.cluster_id])
        f.write(f"- **Unassigned Complaints:** {unclustered}\n\n")
        
        for c in clusters:
            f.write(f"### {c.title}\n")
            f.write(f"- **Cluster Size:** {c.complaint_count} complaints\n")
            f.write(f"- **Incident Count (Episodes):** {c.incident_count}\n")
            f.write(f"- **Confidence:** {c.confidence} ({c.confidence_level})\n")
            f.write(f"- **Evidence Strength:** {c.evidence_strength}\n")
            f.write(f"- **Rationale:** {c.cluster_rationale}\n")
            f.write("#### Relationship Evidence\n")
            f.write(f"```json\n{json.dumps(c.relationship_evidence, indent=2)}\n```\n\n")
            
        f.write("## 2. Complaint Diagnostic Table\n")
        f.write("| ID | Category | Reported At | Severity | Assigned Cluster | Reason |\n")
        f.write("|---|---|---|---|---|---|\n")
        for c in complaints:
            cluster_title = db.query(FailureCluster).filter_by(cluster_id=c.cluster_id).first().title if c.cluster_id else "Unclustered"
            f.write(f"| {c.complaint_id[:6]} | {c.category or c.incident_type} | {c.reported_at.date()} | {c.severity} | {cluster_title} | Multi-signal affinity |\n")
            
    db.close()

if __name__ == "__main__":
    main()
