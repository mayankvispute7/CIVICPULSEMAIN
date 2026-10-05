"""
Outcome Service.

Handles:
- Recording outcome observations during comparable future events
- Comparing predicted outcomes vs actual observed reality
- Updating failure cases based on outcomes
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.domain import (
    OutcomeObservation, PredictionRealityComparison, Prediction,
    FailureCase, WorkOrder, InterventionOption
)
from app.models.enums import (
    OutcomeStatus, PredictionComparison, DataTruth, CaseStatus
)

logger = logging.getLogger(__name__)


class OutcomeService:
    """Service for measuring real-world outcomes and comparing to predictions."""

    def __init__(self, db: Session):
        self.db = db

    def record_outcome(
        self,
        case_id: str,
        observed_at: datetime,
        status: str,
        trigger_event: str,
        work_order_id: Optional[str] = None,
        trigger_event_details: Optional[dict] = None,
        observed_conditions: Optional[dict] = None,
        complaints_during_event: int = 0,
        spatial_impact: Optional[dict] = None,
        notes: Optional[str] = None,
    ) -> Optional[OutcomeObservation]:
        """Record a real-world outcome observation."""
        case = self.db.query(FailureCase).filter(FailureCase.case_id == case_id).first()
        if not case:
            return None

        # If no work_order provided, find the most recently completed one
        if not work_order_id:
            wo = self.db.query(WorkOrder).filter(
                WorkOrder.case_id == case_id,
                WorkOrder.status == "COMPLETED"
            ).order_by(WorkOrder.actual_end.desc()).first()
            if wo:
                work_order_id = wo.work_order_id

        outcome = OutcomeObservation(
            case_id=case_id,
            work_order_id=work_order_id,
            observed_at=observed_at,
            status=status,
            trigger_event=trigger_event,
            trigger_event_details=trigger_event_details or {},
            observed_conditions=observed_conditions or {},
            complaints_during_event=complaints_during_event,
            spatial_impact=spatial_impact or {},
            notes=notes,
            data_truth=DataTruth.EVIDENCE.value,
        )
        self.db.add(outcome)
        self.db.flush()

        # Update case status if resolved
        if status == OutcomeStatus.IMPROVED.value and complaints_during_event == 0:
            case.status = CaseStatus.CLOSED.value
            
        # Automatically run prediction vs reality comparison
        self._compare_predictions(case_id, outcome)

        self.db.commit()
        return outcome

    def _compare_predictions(self, case_id: str, outcome: OutcomeObservation):
        """Compare all active predictions for this case against the observed outcome."""
        predictions = self.db.query(Prediction).filter(
            Prediction.case_id == case_id
        ).all()
        
        # Only compare predictions linked to the executed intervention
        wo = None
        if outcome.work_order_id:
            wo = self.db.query(WorkOrder).filter(WorkOrder.work_order_id == outcome.work_order_id).first()
            
        if wo:
            predictions = [p for p in predictions if p.intervention_id == wo.intervention_id]

        for pred in predictions:
            if pred.predicted_metric == "recurrence_probability":
                observed_val = 1.0 if outcome.status == OutcomeStatus.RECURRENCE.value else 0.0
                
                # Simple evaluation: if probability was < 0.5 and it didn't recur, that's a match.
                # If probability was > 0.5 and it did recur, match. Otherwise mismatch.
                if (pred.predicted_value < 0.5 and observed_val == 0.0) or \
                   (pred.predicted_value >= 0.5 and observed_val == 1.0):
                    result = PredictionComparison.MATCHED.value
                else:
                    result = PredictionComparison.MISMATCHED.value
                    
                error = abs(pred.predicted_value - observed_val)
                
                comp = PredictionRealityComparison(
                    prediction_id=pred.prediction_id,
                    outcome_id=outcome.outcome_id,
                    case_id=case_id,
                    predicted_value=pred.predicted_value,
                    observed_value=observed_val,
                    predicted_metric=pred.predicted_metric,
                    comparison_result=result,
                    error=error,
                    model_version=pred.model_version,
                    confidence=0.8,
                )
                self.db.add(comp)
                
            elif pred.predicted_metric == "expected_months_to_recurrence":
                if outcome.status == OutcomeStatus.RECURRENCE.value:
                    if wo and wo.actual_end:
                        months_elapsed = (outcome.observed_at - wo.actual_end).days / 30.0
                        
                        # Within 20% margin
                        margin = pred.predicted_value * 0.2
                        if abs(months_elapsed - pred.predicted_value) <= margin:
                            result = PredictionComparison.MATCHED.value
                        else:
                            result = PredictionComparison.MISMATCHED.value
                            
                        comp = PredictionRealityComparison(
                            prediction_id=pred.prediction_id,
                            outcome_id=outcome.outcome_id,
                            case_id=case_id,
                            predicted_value=pred.predicted_value,
                            observed_value=months_elapsed,
                            predicted_metric=pred.predicted_metric,
                            comparison_result=result,
                            error=abs(months_elapsed - pred.predicted_value),
                            model_version=pred.model_version,
                            confidence=0.9,
                        )
                        self.db.add(comp)

    def get_outcomes(self, case_id: str) -> list[OutcomeObservation]:
        return self.db.query(OutcomeObservation).filter(
            OutcomeObservation.case_id == case_id
        ).order_by(OutcomeObservation.observed_at.desc()).all()

    def get_comparisons(self, case_id: str) -> list[PredictionRealityComparison]:
        return self.db.query(PredictionRealityComparison).filter(
            PredictionRealityComparison.case_id == case_id
        ).order_by(PredictionRealityComparison.comparison_date.desc()).all()
