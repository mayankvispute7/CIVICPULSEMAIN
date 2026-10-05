"""
Execution Service.

Handles:
- Work order creation from approved resolution plans
- Task management (create, start, complete, delay, block)
- Execution event recording
- Dynamic replanning when delays occur
- Schedule recalculation
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.domain import (
    WorkOrder, WorkOrderTask, ExecutionEvent, ReplanEvent,
    ResolutionPlan, InterventionOption, FailureCase
)
from app.models.enums import (
    WorkOrderStatus, TaskStatus, ExecutionEventType,
    ApprovalState, CaseStatus
)

logger = logging.getLogger(__name__)


class ExecutionService:
    """Service for work order execution and dynamic replanning."""

    def __init__(self, db: Session):
        self.db = db

    def create_work_order(self, plan_id: str) -> Optional[WorkOrder]:
        """Create a work order from an approved resolution plan."""
        plan = self.db.query(ResolutionPlan).filter(
            ResolutionPlan.plan_id == plan_id
        ).first()

        if not plan:
            logger.error(f"Plan not found: {plan_id}")
            return None

        if plan.approval_state != ApprovalState.APPROVED.value:
            logger.error(f"Plan not approved: {plan_id}")
            return None

        intervention = self.db.query(InterventionOption).filter(
            InterventionOption.intervention_id == plan.intervention_id
        ).first()

        case = self.db.query(FailureCase).filter(
            FailureCase.case_id == plan.case_id
        ).first()

        now = datetime.utcnow()
        planned_end = now + timedelta(days=plan.total_duration_days)

        work_order = WorkOrder(
            plan_id=plan_id,
            intervention_id=plan.intervention_id,
            case_id=plan.case_id,
            title=plan.title.replace("Resolution Plan", "Work Order"),
            description=plan.description,
            status=WorkOrderStatus.PENDING.value,
            approval_state=ApprovalState.APPROVED.value,
            approved_by=plan.approved_by,
            approved_at=plan.approved_at,
            planned_start=now,
            planned_end=planned_end,
            location_lat=case.site.latitude if case and case.site else None,
            location_lon=case.site.longitude if case and case.site else None,
        )
        self.db.add(work_order)
        self.db.flush()

        # Create tasks from plan phases
        self._create_tasks_from_plan(work_order, plan)

        # Update case status
        if case:
            case.status = CaseStatus.EXECUTING.value

        # Record event
        event = ExecutionEvent(
            work_order_id=work_order.work_order_id,
            event_type=ExecutionEventType.APPROVAL_GRANTED.value,
            description="Work order created from approved resolution plan",
            new_value={"plan_id": plan_id, "status": "PENDING"},
            timestamp=now,
        )
        self.db.add(event)

        self.db.commit()
        logger.info(f"Created work order {work_order.work_order_id} from plan {plan_id}")
        return work_order

    def _create_tasks_from_plan(self, work_order: WorkOrder, plan: ResolutionPlan):
        """Create work order tasks from a resolution plan's phases."""
        current_start = datetime.utcnow()
        all_tasks = []

        for phase in plan.phases:
            for task_def in phase.get("tasks", []):
                duration_hours = task_def.get("duration_hours", 4)
                task_end = current_start + timedelta(hours=duration_hours)

                task = WorkOrderTask(
                    work_order_id=work_order.work_order_id,
                    title=task_def.get("title", f"Task {task_def.get('sequence', 0)}"),
                    description=f"Phase: {phase.get('title', 'Unknown')}",
                    sequence=task_def.get("sequence", 0),
                    status=TaskStatus.PENDING.value,
                    planned_duration_hours=duration_hours,
                    planned_start=current_start,
                    planned_end=task_end,
                    dependencies=[t.task_id for t in all_tasks[-1:]] if all_tasks else [],
                )
                self.db.add(task)
                self.db.flush()
                all_tasks.append(task)
                current_start = task_end

    def approve_plan(self, plan_id: str, approved_by: str) -> Optional[ResolutionPlan]:
        """Approve a resolution plan (human approval step)."""
        plan = self.db.query(ResolutionPlan).filter(
            ResolutionPlan.plan_id == plan_id
        ).first()

        if not plan:
            return None

        plan.approval_state = ApprovalState.APPROVED.value
        plan.approved_by = approved_by
        plan.approved_at = datetime.utcnow()
        self.db.commit()
        return plan

    def reject_plan(self, plan_id: str, rejected_by: str) -> Optional[ResolutionPlan]:
        """Reject a resolution plan."""
        plan = self.db.query(ResolutionPlan).filter(
            ResolutionPlan.plan_id == plan_id
        ).first()

        if not plan:
            return None

        plan.approval_state = ApprovalState.REJECTED.value
        plan.approved_by = rejected_by
        plan.approved_at = datetime.utcnow()
        self.db.commit()
        return plan

    def start_task(self, task_id: str) -> Optional[WorkOrderTask]:
        """Start a task execution."""
        task = self.db.query(WorkOrderTask).filter(
            WorkOrderTask.task_id == task_id
        ).first()

        if not task:
            return None

        now = datetime.utcnow()
        old_status = task.status
        task.status = TaskStatus.IN_PROGRESS.value
        task.actual_start = now
        task.updated_at = now

        # Update work order status if needed
        work_order = task.work_order
        if work_order and work_order.status == WorkOrderStatus.PENDING.value:
            work_order.status = WorkOrderStatus.IN_PROGRESS.value
            work_order.actual_start = now

        # Record event
        event = ExecutionEvent(
            work_order_id=task.work_order_id,
            task_id=task_id,
            event_type=ExecutionEventType.TASK_STARTED.value,
            description=f"Task started: {task.title}",
            old_value={"status": old_status},
            new_value={"status": task.status},
            timestamp=now,
        )
        self.db.add(event)
        self.db.commit()
        return task

    def complete_task(self, task_id: str, notes: Optional[str] = None) -> Optional[WorkOrderTask]:
        """Mark a task as completed."""
        task = self.db.query(WorkOrderTask).filter(
            WorkOrderTask.task_id == task_id
        ).first()

        if not task:
            return None

        now = datetime.utcnow()
        task.status = TaskStatus.COMPLETED.value
        task.actual_end = now
        task.completion_percentage = 100.0
        if task.actual_start:
            task.actual_duration_hours = (now - task.actual_start).total_seconds() / 3600
        if notes:
            task.notes = notes
        task.updated_at = now

        # Check if all tasks are complete → complete work order
        self._check_work_order_completion(task.work_order_id)

        # Record event
        event = ExecutionEvent(
            work_order_id=task.work_order_id,
            task_id=task_id,
            event_type=ExecutionEventType.TASK_COMPLETED.value,
            description=f"Task completed: {task.title}",
            new_value={"status": "COMPLETED", "actual_duration_hours": task.actual_duration_hours},
            timestamp=now,
        )
        self.db.add(event)
        self.db.commit()
        return task

    def delay_task(
        self,
        task_id: str,
        delay_reason: str,
        delay_hours: float = 0,
    ) -> Optional[dict]:
        """Record a task delay and trigger replanning if needed."""
        task = self.db.query(WorkOrderTask).filter(
            WorkOrderTask.task_id == task_id
        ).first()

        if not task:
            return None

        now = datetime.utcnow()
        old_end = task.planned_end
        task.delay_reason = delay_reason
        task.status = TaskStatus.BLOCKED.value if delay_hours > 4 else TaskStatus.IN_PROGRESS.value
        task.updated_at = now

        # Record delay event
        event = ExecutionEvent(
            work_order_id=task.work_order_id,
            task_id=task_id,
            event_type=ExecutionEventType.TASK_DELAYED.value,
            description=f"Task delayed: {delay_reason}",
            old_value={"planned_end": old_end.isoformat() if old_end else None},
            new_value={"delay_hours": delay_hours, "reason": delay_reason},
            timestamp=now,
        )
        self.db.add(event)

        # Trigger replanning
        replan = self._trigger_replan(task, delay_hours, delay_reason)

        self.db.commit()

        return {
            "task": task,
            "replan": replan,
            "event": event,
        }

    def _trigger_replan(
        self,
        delayed_task: WorkOrderTask,
        delay_hours: float,
        reason: str,
    ) -> ReplanEvent:
        """Trigger dynamic replanning due to a delay."""
        work_order = delayed_task.work_order
        all_tasks = self.db.query(WorkOrderTask).filter(
            WorkOrderTask.work_order_id == delayed_task.work_order_id,
        ).order_by(WorkOrderTask.sequence).all()

        # Calculate impact on remaining schedule
        affected_tasks = []
        delay_delta = timedelta(hours=delay_hours)

        for task in all_tasks:
            if task.sequence > delayed_task.sequence and task.status in (
                TaskStatus.PENDING.value, TaskStatus.READY.value
            ):
                # Shift planned times
                old_start = task.planned_start
                old_end = task.planned_end
                if task.planned_start:
                    task.planned_start = task.planned_start + delay_delta
                if task.planned_end:
                    task.planned_end = task.planned_end + delay_delta

                affected_tasks.append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "old_planned_start": old_start.isoformat() if old_start else None,
                    "new_planned_start": task.planned_start.isoformat() if task.planned_start else None,
                    "old_planned_end": old_end.isoformat() if old_end else None,
                    "new_planned_end": task.planned_end.isoformat() if task.planned_end else None,
                })

        # Check deadline risk
        deadline_risk = "LOW"
        if work_order and work_order.planned_end:
            last_task = all_tasks[-1] if all_tasks else None
            if last_task and last_task.planned_end and last_task.planned_end > work_order.planned_end:
                deadline_risk = "HIGH"
                work_order.planned_end = last_task.planned_end + timedelta(hours=4)
            elif delay_hours > 8:
                deadline_risk = "MEDIUM"

        # Generate recommended actions
        recommended_actions = []
        if deadline_risk == "HIGH":
            recommended_actions.extend([
                "Consider additional crew to accelerate remaining tasks",
                "Evaluate task parallelization opportunities",
                "Consider alternative resource allocation",
                "Escalate deadline risk to supervisor",
            ])
        elif deadline_risk == "MEDIUM":
            recommended_actions.extend([
                "Monitor subsequent tasks for further delays",
                "Pre-stage materials for next tasks to minimize transition time",
            ])

        replan = ReplanEvent(
            work_order_id=delayed_task.work_order_id,
            reason=reason,
            trigger_event_id=delayed_task.task_id,
            previous_plan={
                "original_completion": work_order.planned_end.isoformat() if work_order and work_order.planned_end else None,
            },
            new_plan={
                "revised_completion": (
                    work_order.planned_end.isoformat()
                    if work_order and work_order.planned_end else None
                ),
                "delay_hours": delay_hours,
            },
            affected_tasks=affected_tasks,
            deadline_risk=deadline_risk,
            recommended_actions=recommended_actions,
            requires_human_approval=deadline_risk in ("HIGH",),
        )
        self.db.add(replan)
        self.db.flush()

        return replan

    def _check_work_order_completion(self, work_order_id: str):
        """Check if all tasks are complete and update work order accordingly."""
        tasks = self.db.query(WorkOrderTask).filter(
            WorkOrderTask.work_order_id == work_order_id
        ).all()

        all_complete = all(
            t.status in (TaskStatus.COMPLETED.value, TaskStatus.SKIPPED.value, TaskStatus.CANCELLED.value)
            for t in tasks
        )

        if all_complete:
            work_order = self.db.query(WorkOrder).filter(
                WorkOrder.work_order_id == work_order_id
            ).first()
            if work_order:
                work_order.status = WorkOrderStatus.COMPLETED.value
                work_order.actual_end = datetime.utcnow()

    # ─────────────────────────────────────────────────────────
    # Query methods
    # ─────────────────────────────────────────────────────────

    def get_work_order(self, work_order_id: str) -> Optional[WorkOrder]:
        return self.db.query(WorkOrder).filter(
            WorkOrder.work_order_id == work_order_id
        ).first()

    def get_work_orders(self, case_id: Optional[str] = None) -> list[WorkOrder]:
        q = self.db.query(WorkOrder)
        if case_id:
            q = q.filter(WorkOrder.case_id == case_id)
        return q.order_by(WorkOrder.created_at.desc()).all()

    def get_tasks(self, work_order_id: str) -> list[WorkOrderTask]:
        return self.db.query(WorkOrderTask).filter(
            WorkOrderTask.work_order_id == work_order_id
        ).order_by(WorkOrderTask.sequence).all()

    def get_task(self, task_id: str) -> Optional[WorkOrderTask]:
        return self.db.query(WorkOrderTask).filter(
            WorkOrderTask.task_id == task_id
        ).first()

    def get_execution_events(self, work_order_id: str) -> list[ExecutionEvent]:
        return self.db.query(ExecutionEvent).filter(
            ExecutionEvent.work_order_id == work_order_id
        ).order_by(ExecutionEvent.timestamp).all()

    def get_replan_events(self, work_order_id: str) -> list[ReplanEvent]:
        return self.db.query(ReplanEvent).filter(
            ReplanEvent.work_order_id == work_order_id
        ).order_by(ReplanEvent.created_at.desc()).all()

    def update_task(self, task_id: str, updates: dict) -> Optional[WorkOrderTask]:
        """Generic task update."""
        task = self.get_task(task_id)
        if not task:
            return None

        for key, value in updates.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        self.db.commit()
        return task
