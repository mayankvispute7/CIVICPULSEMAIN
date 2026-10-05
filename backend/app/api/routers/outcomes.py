"""Router for outcome tracking and infrastructure memory."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.outcome_service import OutcomeService
from app.services.learning_service import LearningService
from app.schemas.api_schemas import (
    OutcomeRequest, OutcomeResponse, PredictionRealityResponse,
    LearningRecordResponse, InfrastructureMemoryResponse
)

router = APIRouter(prefix="/outcomes", tags=["outcomes"])

@router.post("", response_model=OutcomeResponse)
def record_outcome(req: OutcomeRequest, db: Session = Depends(get_db)):
    """Record a real-world outcome observation (e.g. after next rainfall)."""
    service = OutcomeService(db)
    outcome = service.record_outcome(
        case_id=req.case_id,
        observed_at=req.observed_at,
        status=req.status,
        trigger_event=req.trigger_event,
        work_order_id=req.work_order_id,
        trigger_event_details=req.trigger_event_details,
        observed_conditions=req.observed_conditions,
        complaints_during_event=req.complaints_during_event,
        spatial_impact=req.spatial_impact,
        notes=req.notes,
    )
    if not outcome:
        raise HTTPException(status_code=404, detail="Case not found")
    return outcome

@router.get("/cases/{case_id}", response_model=list[OutcomeResponse])
def get_outcomes(case_id: str, db: Session = Depends(get_db)):
    """Get all recorded outcomes for a case."""
    service = OutcomeService(db)
    return service.get_outcomes(case_id)

@router.get("/cases/{case_id}/comparisons", response_model=list[PredictionRealityResponse])
def get_comparisons(case_id: str, db: Session = Depends(get_db)):
    """Get prediction vs reality comparison results."""
    service = OutcomeService(db)
    return service.get_comparisons(case_id)

@router.post("/comparisons/{comparison_id}/learn", response_model=LearningRecordResponse)
def generate_learning(comparison_id: str, db: Session = Depends(get_db)):
    """Extract learning record from a prediction comparison."""
    service = LearningService(db)
    learning = service.generate_learning(comparison_id)
    if not learning:
        raise HTTPException(status_code=404, detail="Comparison or Case not found")
    return learning

@router.get("/cases/{case_id}/learnings", response_model=list[LearningRecordResponse])
def get_case_learnings(case_id: str, db: Session = Depends(get_db)):
    """Get learning records for a case."""
    service = LearningService(db)
    return service.get_learnings(case_id)

@router.get("/sites/{site_id}/memory", response_model=InfrastructureMemoryResponse)
def get_infrastructure_memory(site_id: str, db: Session = Depends(get_db)):
    """Get the comprehensive long-term infrastructure memory for a site."""
    service = LearningService(db)
    memory = service.get_memory(site_id)
    if not memory:
        # Generate it on demand if missing but site exists
        try:
            memory = service.update_site_memory(site_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Site not found")
    return memory
