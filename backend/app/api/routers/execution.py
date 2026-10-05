"""Router for execution and verification endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.execution_service import ExecutionService
from app.services.verification_service import VerificationService
from app.schemas.api_schemas import (
    WorkOrderResponse, TaskResponse, TaskUpdateRequest,
    ExecutionEventResponse, ReplanEventResponse, ApprovalRequest,
    FieldEvidenceRequest, FieldEvidenceResponse, VerificationResponse,
    ResolutionPlanResponse, TaskDelayResponse
)

router = APIRouter(prefix="/execution", tags=["execution"])

@router.post("/plans/{plan_id}/approve", response_model=ResolutionPlanResponse)
def approve_plan(plan_id: str, req: ApprovalRequest, db: Session = Depends(get_db)):
    """Human approval for a resolution plan."""
    service = ExecutionService(db)
    if req.decision.upper() == "APPROVED":
        plan = service.approve_plan(plan_id, req.approved_by)
    else:
        plan = service.reject_plan(plan_id, req.approved_by)
        
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.post("/plans/{plan_id}/work-order", response_model=WorkOrderResponse)
def create_work_order(plan_id: str, db: Session = Depends(get_db)):
    """Dispatch an approved plan into a work order."""
    service = ExecutionService(db)
    wo = service.create_work_order(plan_id)
    if not wo:
        raise HTTPException(status_code=400, detail="Plan not found or not approved")
    return wo

@router.get("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(work_order_id: str, db: Session = Depends(get_db)):
    """Get work order details."""
    service = ExecutionService(db)
    wo = service.get_work_order(work_order_id)
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    return wo

@router.get("/work-orders/{work_order_id}/tasks", response_model=list[TaskResponse])
def get_tasks(work_order_id: str, db: Session = Depends(get_db)):
    """Get all tasks for a work order."""
    service = ExecutionService(db)
    return service.get_tasks(work_order_id)

@router.post("/tasks/{task_id}/start", response_model=TaskResponse)
def start_task(task_id: str, db: Session = Depends(get_db)):
    """Start execution of a task."""
    service = ExecutionService(db)
    task = service.start_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str, notes: str = Body(None, embed=True), db: Session = Depends(get_db)):
    """Mark a task as complete."""
    service = ExecutionService(db)
    task = service.complete_task(task_id, notes)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks/{task_id}/delay", response_model=TaskDelayResponse)
def delay_task(
    task_id: str, 
    reason: str = Body(..., embed=True),
    hours: float = Body(0, embed=True),
    db: Session = Depends(get_db)
):
    """Report a delay/blockage on a task. Triggers dynamic replanning."""
    service = ExecutionService(db)
    result = service.delay_task(task_id, reason, hours)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task": result["task"],
        "replan_event": result["replan"]
    }

@router.get("/work-orders/{work_order_id}/events", response_model=list[ExecutionEventResponse])
def get_execution_events(work_order_id: str, db: Session = Depends(get_db)):
    """Get the execution audit trail."""
    service = ExecutionService(db)
    return service.get_execution_events(work_order_id)

@router.get("/work-orders/{work_order_id}/replans", response_model=list[ReplanEventResponse])
def get_replan_events(work_order_id: str, db: Session = Depends(get_db)):
    """Get dynamic replanning events."""
    service = ExecutionService(db)
    return service.get_replan_events(work_order_id)

# ─────────────────────────────────────────────────────────────
# Verification
# ─────────────────────────────────────────────────────────────

@router.post("/evidence", response_model=FieldEvidenceResponse)
def submit_evidence(req: FieldEvidenceRequest, db: Session = Depends(get_db)):
    """Submit field evidence (photos/GPS) for a task/work order."""
    service = VerificationService(db)
    evidence = service.submit_field_evidence(
        work_order_id=req.work_order_id,
        latitude=req.latitude,
        longitude=req.longitude,
        captured_at=req.captured_at,
        task_id=req.task_id,
        image_url=req.image_url,
        metadata_info=req.metadata_info,
    )
    if not evidence:
        raise HTTPException(status_code=400, detail="Work order not found")
    return evidence

@router.get("/work-orders/{work_order_id}/evidence", response_model=list[FieldEvidenceResponse])
def get_evidence(work_order_id: str, db: Session = Depends(get_db)):
    """Get all field evidence for a work order."""
    service = VerificationService(db)
    return service.get_evidence(work_order_id)

@router.post("/work-orders/{work_order_id}/verify", response_model=VerificationResponse)
def verify_work_order(
    work_order_id: str, 
    verified_by: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Run automated integrity verification on completed work."""
    service = VerificationService(db)
    verification = service.verify_work_order(work_order_id, verified_by)
    if not verification:
        raise HTTPException(status_code=404, detail="Work order not found")
    return verification
