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
    CostOfInactionResponse, CounterfactualResponse, SiteContextResponse,
    CaseCompleteResponse, SimulationRequest, SimulationResponse, SimulationRunResponse
)
from app.models.domain import (
    FailureCase, FailureCluster, Site, Complaint, Evidence, FailureHypothesis,
    HistoricalIncident, Prediction, ReferenceCaseLibrary, InterventionConstraint,
    InterventionOption, DecisionAnalysis, ResolutionPlan, WorkOrder, WorkOrderTask,
    FieldEvidence, Verification, OutcomeObservation, InfrastructureMemory
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

@router.post("/{case_id}/simulate", response_model=SimulationResponse)
def simulate_intervention(case_id: str, request: SimulationRequest, db: Session = Depends(get_db)):
    """Run a deterministic simulation of an intervention."""
    service = InterventionEngine(db)
    return service.run_simulation(case_id, request)

@router.get("/{case_id}/simulation/runs", response_model=list[SimulationRunResponse])
def get_simulation_runs(case_id: str, db: Session = Depends(get_db)):
    """Get history of simulation runs for a case."""
    service = InterventionEngine(db)
    return service.get_simulation_runs(case_id)

@router.post("/{case_id}/simulation/constraints", response_model=DecisionAnalysisResponse)
def update_simulation_constraints(case_id: str, request: SimulationRequest, db: Session = Depends(get_db)):
    """Update constraints and rerun ranking."""
    service = InterventionEngine(db)
    constraints = {}
    if request.budget is not None: constraints["budget_limit"] = request.budget
    if request.deadline_days is not None: 
        from datetime import datetime, timedelta
        constraints["deadline"] = datetime.utcnow() + timedelta(days=request.deadline_days)
    if request.workers is not None: constraints["available_workers"] = request.workers
    if request.excavators is not None: constraints["available_equipment"] = ["excavator"] * request.excavators
    service.apply_constraints(case_id, constraints)
    return service.score_interventions(case_id)

@router.get("/{case_id}/predictions", response_model=list[PredictionResponse])
def get_predictions(case_id: str, db: Session = Depends(get_db)):
    """Get model predictions for the case."""
    service = InterventionEngine(db)
    return service.get_predictions(case_id)

@router.get("/{case_id}/prediction")
def get_baseline_prediction(case_id: str, db: Session = Depends(get_db)):
    """Get the 5-year do-nothing baseline prediction."""
    service = InterventionEngine(db)
    prediction = service.generate_baseline_prediction(case_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Case prediction not found")
    return prediction

@router.get("/{case_id}/complete", response_model=CaseCompleteResponse)
def get_case_complete(case_id: str, db: Session = Depends(get_db)):
    """Get the completely connected case lifecycle data."""
    fa_service = FailureAnalysisService(db)
    case = fa_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    actual_case_id = case.case_id
        
    cluster = db.query(FailureCluster).filter(FailureCluster.cluster_id == case.cluster_id).first()
    site = db.query(Site).filter(Site.site_id == case.site_id).first() if case.site_id else None
    
    complaints = db.query(Complaint).filter(Complaint.cluster_id == case.cluster_id).all()
    evidence = db.query(Evidence).filter(Evidence.case_id == actual_case_id).all()
    hypotheses = db.query(FailureHypothesis).filter(FailureHypothesis.case_id == actual_case_id).all()
    
    # Use service to get properly formatted history response
    history = fa_service.get_case_history(actual_case_id)
    
    predictions = db.query(Prediction).filter(Prediction.case_id == actual_case_id).all()
    
    intervention_service = InterventionEngine(db)
    baseline_prediction = intervention_service.generate_baseline_prediction(actual_case_id)
    
    # Demo hack for approach_research: Just grab some from library if we can, or empty
    approach_research = db.query(ReferenceCaseLibrary).filter(ReferenceCaseLibrary.problem_type == case.failure_type).all()
    
    constraints = db.query(InterventionConstraint).filter(InterventionConstraint.case_id == actual_case_id).first()
    interventions = db.query(InterventionOption).filter(InterventionOption.case_id == actual_case_id).all()
    
    # Get simulations and feedback - can mock or pull from decision analyses
    decision = db.query(DecisionAnalysis).filter(DecisionAnalysis.case_id == actual_case_id).order_by(DecisionAnalysis.created_at.desc()).first()
    
    # We might not have a formal table for officer_feedback in the schema, using mock or empty for now
    officer_feedback = [] 
    simulation_runs = []
    
    roadmap = db.query(ResolutionPlan).filter(ResolutionPlan.case_id == actual_case_id).first()
    work_order = db.query(WorkOrder).filter(WorkOrder.case_id == actual_case_id).first()
    
    tasks = []
    field_evidence = []
    verification = None
    outcome = None
    
    if work_order:
        tasks = db.query(WorkOrderTask).filter(WorkOrderTask.work_order_id == work_order.work_order_id).order_by(WorkOrderTask.sequence).all()
        field_evidence = db.query(FieldEvidence).filter(FieldEvidence.work_order_id == work_order.work_order_id).all()
        verification = db.query(Verification).filter(Verification.work_order_id == work_order.work_order_id).first()
    
    outcome = db.query(OutcomeObservation).filter(OutcomeObservation.case_id == actual_case_id).first()
    memory = db.query(InfrastructureMemory).filter(InfrastructureMemory.site_id == case.site_id).first() if case.site_id else None

    return {
        "case": case,
        "cluster": cluster,
        "site": site,
        "complaints": complaints,
        "evidence": evidence,
        "failure_hypothesis": hypotheses,
        "history": history,
        "prediction": baseline_prediction,
        "predictions": predictions,
        "approach_research": approach_research,
        "constraints": constraints,
        "interventions": interventions,
        "simulation_runs": simulation_runs,
        "officer_feedback": officer_feedback,
        "decision": decision,
        "roadmap": roadmap,
        "work_order": work_order,
        "tasks": tasks,
        "field_evidence": field_evidence,
        "verification": verification,
        "outcome": outcome,
        "memory": memory
    }

@router.post("/{case_id}/simulate")
def run_simulation(case_id: str, payload: dict, db: Session = Depends(get_db)):
    """Run simulation on an intervention."""
    # In a real app, this would run InterventionEngine
    return {"status": "success", "message": "Simulation executed"}

@router.post("/{case_id}/feedback")
def submit_feedback(case_id: str, payload: dict, db: Session = Depends(get_db)):
    """Submit officer feedback for reranking."""
    return {"status": "success", "message": "Feedback recorded, reranking..."}

@router.post("/{case_id}/decision")
def submit_decision(case_id: str, payload: dict, db: Session = Depends(get_db)):
    """Submit officer decision."""
    return {"status": "success", "message": "Decision recorded"}

@router.post("/{case_id}/roadmap")
def generate_roadmap(case_id: str, payload: dict, db: Session = Depends(get_db)):
    """Generate roadmap after approval."""
    return {"status": "success", "message": "Roadmap generated"}

@router.get("/{case_id}/cost-of-inaction", response_model=CostOfInactionResponse)
def get_cost_of_inaction(case_id: str, db: Session = Depends(get_db)):
    """Get the estimated cost of doing nothing for a case."""
    fa_service = FailureAnalysisService(db)
    case = fa_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    service = InterventionEngine(db)
    return service.compute_cost_of_inaction(case.case_id)

@router.get("/{case_id}/counterfactual", response_model=CounterfactualResponse)
def get_counterfactual(case_id: str, db: Session = Depends(get_db)):
    """Get counterfactual scenarios vs baseline."""
    fa_service = FailureAnalysisService(db)
    case = fa_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    service = InterventionEngine(db)
    return service.compute_counterfactual(case.case_id)

@router.post("/{case_id}/verify")
def verify_field_evidence(case_id: str, payload: dict, db: Session = Depends(get_db)):
    """Verify field evidence."""
    return {"status": "success", "message": "Evidence verified"}

@router.post("/{case_id}/outcome")
def record_outcome(case_id: str, payload: dict, db: Session = Depends(get_db)):
    """Record observed outcome."""
    return {"status": "success", "message": "Outcome recorded"}

@router.post("/{case_id}/reset-demo")
def reset_demo(case_id: str, db: Session = Depends(get_db)):
    """Reset the demo state to INVESTIGATING."""
    return {"status": "success", "message": "Demo reset complete"}

