import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.clustering_service import ClusteringService
from app.models.domain import Complaint

def analyze_clustering():
    db = SessionLocal()
    service = ClusteringService(db)
    
    # Run clustering
    result = service.run_clustering()
    
    print("==================================================")
    print("CLUSTERING DIAGNOSTIC REPORT")
    print("==================================================")
    print(f"Total Complaints: {result['total_complaints']}")
    print(f"Total Clusters: {result['total_clusters']}")
    
    for cluster in result['clusters']:
        print("\n--------------------------------------------------")
        print(f"CLUSTER: {cluster.title} ({cluster.cluster_id})")
        print(f"Complaints: {cluster.complaint_count}")
        print(f"Incident Episodes: {cluster.incident_count}")
        print(f"Confidence: {cluster.confidence:.2f}")
        print(f"Semantic Similarity: {cluster.semantic_similarity:.2f}")
        print(f"Spatial Radius: {cluster.spatial_radius_m:.1f}m")
        time_span = (cluster.time_range_end - cluster.time_range_start).days if cluster.time_range_end else 0
        print(f"Time Span: {time_span} days")
        
        print("\nCOMPLAINTS IN CLUSTER:")
        complaints = service.get_cluster_complaints(cluster.cluster_id)
        
        print(f"{'ID':<15} | {'Category':<22} | {'Severity':<8} | {'Date':<10} | {'Distance (m)':<12}")
        print("-" * 75)
        
        for c in sorted(complaints, key=lambda x: x.reported_at):
            # Calculate distance to centroid
            from geopy.distance import geodesic
            dist = geodesic((c.latitude, c.longitude), (cluster.centroid_lat, cluster.centroid_lon)).meters
            date_str = c.reported_at.strftime('%Y-%m-%d')
            cat = (c.category or c.incident_type)[:20]
            print(f"{c.complaint_id:<15} | {cat:<22} | {c.severity:<8} | {date_str:<10} | {dist:.1f}m")
            
    db.close()

if __name__ == "__main__":
    analyze_clustering()
