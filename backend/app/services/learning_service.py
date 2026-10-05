"""
Learning Service.

Handles:
- Extracting insights from Prediction vs Reality comparisons
- Updating system confidence in hypotheses/interventions
- Generating and updating Infrastructure Memory for sites
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.domain import (
    LearningRecord, InfrastructureMemory, Site, FailureCase,
    WorkOrder, OutcomeObservation, PredictionRealityComparison,
    Complaint, InterventionOption
)
from app.models.enums import DataTruth, PredictionComparison, OutcomeStatus

logger = logging.getLogger(__name__)


class LearningService:
    """Service for long-term learning and infrastructure memory."""

    def __init__(self, db: Session):
        self.db = db

    def generate_learning(self, comparison_id: str) -> Optional[LearningRecord]:
        """Generate a learning record from a prediction comparison."""
        comp = self.db.query(PredictionRealityComparison).filter(
            PredictionRealityComparison.comparison_id == comparison_id
        ).first()

        if not comp:
            return None
            
        case = self.db.query(FailureCase).filter(FailureCase.case_id == comp.case_id).first()
        if not case:
            return None

        # Find the intervention
        pred = self.db.query(InterventionOption).join(
            WorkOrder, WorkOrder.intervention_id == InterventionOption.intervention_id
        ).join(
            OutcomeObservation, OutcomeObservation.work_order_id == WorkOrder.work_order_id
        ).filter(
            OutcomeObservation.outcome_id == comp.outcome_id
        ).first()
        
        intervention_type = pred.intervention_type if pred else None
        
        # Determine learning type and logic
        title = ""
        desc = ""
        effectiveness = None
        recommendations = []
        
        if comp.comparison_result == PredictionComparison.MATCHED.value:
            if comp.predicted_metric == "recurrence_probability" and comp.predicted_value < 0.5:
                # Intervention worked as predicted
                title = "Intervention Success Validated"
                desc = f"The {intervention_type or 'intervention'} successfully prevented recurrence as predicted."
                effectiveness = 0.9
                recommendations.append(f"Increase confidence for {intervention_type} in similar terrain/drainage contexts.")
            else:
                title = "Prediction Model Validated"
                desc = "The model correctly predicted the outcome metric."
        else:
            if comp.predicted_metric == "recurrence_probability" and comp.predicted_value < 0.5:
                # Expected success, but failed
                title = "Intervention Underperformance"
                desc = f"The {intervention_type or 'intervention'} failed to prevent recurrence despite positive prediction."
                effectiveness = 0.2
                recommendations.append(f"Review capacity assumptions for {intervention_type}.")
                recommendations.append("Consider upgrading to a higher-tier intervention for this site.")
            
        learning = LearningRecord(
            case_id=comp.case_id,
            site_id=case.site_id,
            comparison_id=comparison_id,
            learning_type="intervention_effectiveness",
            title=title or "Outcome Analysis",
            description=desc,
            intervention_type=intervention_type,
            effectiveness_rating=effectiveness,
            recommendations=recommendations,
            data_truth=DataTruth.MODEL_ESTIMATION.value,
        )
        self.db.add(learning)
        
        # Update site memory
        if case.site_id:
            self.update_site_memory(case.site_id)
            
        self.db.commit()
        return learning

    def update_site_memory(self, site_id: str) -> InfrastructureMemory:
        """Create or update the comprehensive long-term memory for a site."""
        site = self.db.query(Site).filter(Site.site_id == site_id).first()
        if not site:
            raise ValueError(f"Site {site_id} not found")
            
        memory = self.db.query(InfrastructureMemory).filter(
            InfrastructureMemory.site_id == site_id
        ).first()
        
        if not memory:
            memory = InfrastructureMemory(
                site_id=site_id,
                title=f"Infrastructure Memory: {site.site_label}",
                total_complaints=0,
                total_cases=0,
                total_interventions=0,
                total_recurrences=0,
            )
            self.db.add(memory)
            
        # Aggregate stats
        complaints = self.db.query(Complaint).filter(Complaint.site_id == site_id).all()
        cases = self.db.query(FailureCase).filter(FailureCase.site_id == site_id).all()
        
        memory.total_complaints = len(complaints)
        memory.total_cases = len(cases)
        
        if complaints:
            latest = max(c.reported_at for c in complaints if c.reported_at)
            memory.last_incident_at = latest
            
        # Analyze interventions and outcomes
        successful = []
        failed = []
        timeline = []
        
        for case in cases:
            timeline.append({
                "date": case.created_at.isoformat(),
                "type": "CASE_CREATED",
                "title": case.title,
                "case_id": case.case_id
            })
            
            # Find work orders
            wos = self.db.query(WorkOrder).filter(WorkOrder.case_id == case.case_id).all()
            for wo in wos:
                memory.total_interventions += 1
                if wo.actual_end:
                    memory.last_intervention_at = max(
                        memory.last_intervention_at or wo.actual_end, 
                        wo.actual_end
                    )
                    
                timeline.append({
                    "date": (wo.actual_start or wo.created_at).isoformat(),
                    "type": "WORK_ORDER",
                    "title": wo.title,
                    "status": wo.status
                })
                
            # Find outcomes
            outcomes = self.db.query(OutcomeObservation).filter(OutcomeObservation.case_id == case.case_id).all()
            for out in outcomes:
                if out.status == OutcomeStatus.RECURRENCE.value:
                    memory.total_recurrences += 1
                    
                # Try to link to a work order
                wo = next((w for w in wos if w.work_order_id == out.work_order_id), None)
                if wo:
                    intervention = self.db.query(InterventionOption).filter(
                        InterventionOption.intervention_id == wo.intervention_id
                    ).first()
                    
                    inv_type = intervention.intervention_type if intervention else "Unknown"
                    
                    if out.status == OutcomeStatus.IMPROVED.value:
                        successful.append({
                            "type": inv_type,
                            "date": out.observed_at.isoformat(),
                            "case_id": case.case_id
                        })
                    elif out.status == OutcomeStatus.RECURRENCE.value:
                        failed.append({
                            "type": inv_type,
                            "date": out.observed_at.isoformat(),
                            "case_id": case.case_id
                        })
                        
        memory.successful_interventions = successful
        memory.failed_interventions = failed
        
        # Extract patterns
        patterns = []
        if len(failed) >= 2 and all(f["type"] == failed[0]["type"] for f in failed):
            patterns.append(f"Repeated failure of '{failed[0]['type']}' intervention at this location.")
            
        if memory.total_recurrences > 0:
            patterns.append(f"Site exhibits chronic recurrence ({memory.total_recurrences} observed).")
            
        memory.learned_patterns = patterns
        
        # Sort timeline
        memory.timeline = sorted(timeline, key=lambda x: x["date"], reverse=True)
        
        # Generate summary
        summary = (
            f"Site with {memory.total_complaints} total complaints and {memory.total_cases} investigated cases. "
            f"History of {memory.total_interventions} interventions. "
        )
        if memory.total_recurrences > 0:
            summary += f"High recurrence risk verified by {memory.total_recurrences} field observations."
        elif successful:
            summary += "Recent interventions show successful stabilization."
            
        memory.summary = summary
        memory.updated_at = datetime.utcnow()
        
        self.db.commit()
        return memory

    def get_memory(self, site_id: str) -> Optional[InfrastructureMemory]:
        return self.db.query(InfrastructureMemory).filter(
            InfrastructureMemory.site_id == site_id
        ).first()

    def get_learnings(self, case_id: str) -> list[LearningRecord]:
        return self.db.query(LearningRecord).filter(
            LearningRecord.case_id == case_id
        ).order_by(LearningRecord.created_at.desc()).all()
