"""Router for failure case analysis and interventions."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.failure_analysis_service import FailureAnalysisService
from app.services.intervention_engine import InterventionEngine
from app.schemas.api_schemas import (
    FailureCaseResponse, FailureCaseListResponse, EvidenceResponse,
    HypothesisResponse, HistoryResponse, InterventionResponse,
    ConstraintRequest, ConstraintResponse, DecisionAnalysisResponse,
    PredictionResponse, ResolutionPlanResponse, ApprovalRequest,
    CostOfInactionResponse, CounterfactualResponse, SiteContextResponse
)
from app.services.geospatial_service import GeospatialService

router = APIRouter(prefix="/cases", tags=["analysis"])

@router.post("/from-cluster/{cluster_id}", response_model=FailureCaseResponse)
def create_case_from_cluster(cluster_id: str, db: Session = Depends(get_db)):
    """Create a failure case from a cluster."""
    service = FailureAnalysisService(db)
    case = service.create_case_from_cluster(cluster_id)
    if not case:
        raise HTTPException(status_code=404, detail="Cluster not found or error creating case")
    return case

@router.post("/generate-all", response_model=list[FailureCaseResponse])
def generate_all_cases(db: Session = Depends(get_db)):
    """Auto-generate cases for all confirmed clusters."""
    service = FailureAnalysisService(db)
    return service.create_cases_from_all_clusters()

@router.get("", response_model=FailureCaseListResponse)
def list_cases(db: Session = Depends(get_db)):
    """List all failure cases."""
    service = FailureAnalysisService(db)
    cases = service.get_cases()
    return {"cases": cases, "total": len(cases)}

@router.get("/{case_id}", response_model=FailureCaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    """Get a specific failure case."""
    service = FailureAnalysisService(db)
    case = service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.get("/{case_id}/evidence", response_model=list[EvidenceResponse])
def get_case_evidence(case_id: str, db: Session = Depends(get_db)):
    """Get evidence for a case."""
    service = FailureAnalysisService(db)
    return service.get_case_evidence(case_id)

@router.get("/{case_id}/hypotheses", response_model=list[HypothesisResponse])
def get_case_hypotheses(case_id: str, db: Session = Depends(get_db)):
    """Get root-cause hypotheses for a case."""
    service = FailureAnalysisService(db)
    return service.get_case_hypotheses(case_id)

@router.get("/{case_id}/history", response_model=HistoryResponse)
def get_case_history(case_id: str, db: Session = Depends(get_db)):
    """Get historical incidents and recurrence intervals."""
    service = FailureAnalysisService(db)
    return service.get_case_history(case_id)

@router.get("/{case_id}/site-context", response_model=SiteContextResponse)
def get_case_site_context(case_id: str, level: str = "LOCAL", db: Session = Depends(get_db)):
    """Get spatial context for a case's site."""
    case = FailureAnalysisService(db).get_case(case_id)
    if not case or not case.site_id:
        raise HTTPException(status_code=404, detail="Case or Site not found")
        
    geo_service = GeospatialService(db)
    return geo_service.get_site_context(case.site_id, level)

# ─────────────────────────────────────────────────────────────
# Interventions & Decisions
# ─────────────────────────────────────────────────────────────

@router.post("/{case_id}/interventions/generate", response_model=list[InterventionResponse])
def generate_interventions(case_id: str, db: Session = Depends(get_db)):
    """Generate intervention options for a case."""
    service = InterventionEngine(db)
    return service.generate_interventions(case_id)

@router.get("/{case_id}/interventions", response_model=list[InterventionResponse])
def get_interventions(case_id: str, db: Session = Depends(get_db)):
    """Get existing intervention options."""
    service = InterventionEngine(db)
    return service.get_interventions(case_id)

@router.post("/{case_id}/constraints", response_model=ConstraintResponse)
def apply_constraints(case_id: str, constraints: ConstraintRequest, db: Session = Depends(get_db)):
    """Apply operational constraints to a case."""
    service = InterventionEngine(db)
    return service.apply_constraints(case_id, constraints.model_dump(exclude_unset=True))

@router.post("/{case_id}/analyze", response_model=DecisionAnalysisResponse)
def run_decision_analysis(case_id: str, db: Session = Depends(get_db)):
    """Score and rank interventions based on constraints."""
    service = InterventionEngine(db)
    return service.score_interventions(case_id)

@router.get("/{case_id}/cost-of-inaction", response_model=CostOfInactionResponse)
def get_cost_of_inaction(case_id: str, db: Session = Depends(get_db)):
    """Get the estimated cost of doing nothing."""
    service = InterventionEngine(db)
    return service.compute_cost_of_inaction(case_id)

@router.get("/{case_id}/counterfactual", response_model=CounterfactualResponse)
def get_counterfactual(case_id: str, db: Session = Depends(get_db)):
    """Get counterfactual scenario analysis."""
    service = InterventionEngine(db)
    return service.compute_counterfactual(case_id)

@router.post("/{case_id}/plan/{intervention_id}", response_model=ResolutionPlanResponse)
def create_resolution_plan(case_id: str, intervention_id: str, db: Session = Depends(get_db)):
    """Select an intervention and generate a resolution plan."""
    service = InterventionEngine(db)
    
    # Generate predictions first
    service.create_predictions(case_id)
    
    plan = service.create_resolution_plan(case_id, intervention_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Case or intervention not found")
    return plan

@router.get("/{case_id}/plan", response_model=ResolutionPlanResponse)
def get_resolution_plan(case_id: str, db: Session = Depends(get_db)):
    """Get the active resolution plan for a case."""
    service = InterventionEngine(db)
    plan = service.get_resolution_plan(case_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.get("/{case_id}/predictions", response_model=list[PredictionResponse])
def get_predictions(case_id: str, db: Session = Depends(get_db)):
    """Get model predictions for the case."""
    service = InterventionEngine(db)
    return service.get_predictions(case_id)
