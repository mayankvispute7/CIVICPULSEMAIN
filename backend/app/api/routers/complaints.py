"""Router for complaint and clustering endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.dependencies import get_db
from app.services.clustering_service import ClusteringService
from app.schemas.api_schemas import (
    ComplaintResponse, ComplaintListResponse, 
    ClusterResponse, ClusterListResponse, ClusteringResultResponse,
    SiteContextResponse
)
from app.models.domain import Complaint

router = APIRouter(prefix="/complaints", tags=["complaints"])

@router.get("", response_model=ComplaintListResponse)
def list_complaints(
    page: int = 1,
    page_size: int = 50,
    status: Optional[str] = None,
    ward: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List complaints with filtering and pagination."""
    query = db.query(Complaint)
    
    if status:
        query = query.filter(Complaint.status == status)
    if ward:
        query = query.filter(Complaint.ward == ward)
    if category:
        query = query.filter(Complaint.category == category)
        
    total = query.count()
    
    complaints = query.order_by(desc(Complaint.reported_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "complaints": complaints,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    """Get a specific complaint."""
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@router.post("/cluster", response_model=ClusteringResultResponse)
def trigger_clustering(
    spatial_eps_m: Optional[float] = Query(None, description="Spatial radius in meters"),
    min_samples: Optional[int] = Query(None, description="Minimum complaints to form a cluster"),
    temporal_days: Optional[int] = Query(None, description="Maximum days between complaints in a cluster"),
    db: Session = Depends(get_db)
):
    """Run clustering algorithm on unclustered complaints."""
    service = ClusteringService(db)
    result = service.run_clustering(spatial_eps_m, min_samples, temporal_days)
    
    # Also trigger case creation for the new clusters
    from app.services.failure_analysis_service import FailureAnalysisService
    fa_service = FailureAnalysisService(db)
    fa_service.create_cases_from_all_clusters()
    
    return result

@router.get("/clusters/all", response_model=ClusterListResponse)
def list_clusters(db: Session = Depends(get_db)):
    """List all identified failure clusters."""
    service = ClusteringService(db)
    clusters = service.get_clusters()
    return {
        "clusters": clusters,
        "total": len(clusters)
    }

@router.get("/clusters/{cluster_id}", response_model=ClusterResponse)
def get_cluster(cluster_id: str, db: Session = Depends(get_db)):
    """Get a specific cluster."""
    service = ClusteringService(db)
    cluster = service.get_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@router.get("/clusters/{cluster_id}/complaints", response_model=list[ComplaintResponse])
def get_cluster_complaints(cluster_id: str, db: Session = Depends(get_db)):
    """Get all complaints within a specific cluster."""
    service = ClusteringService(db)
    return service.get_cluster_complaints(cluster_id)
