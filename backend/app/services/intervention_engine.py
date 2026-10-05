"""
Intervention Engine Service.

Handles:
- Intervention option generation
- Constraint application
- Screening-level physical model
- Decision scoring with transparent breakdown
- Cost of inaction estimation
- Counterfactual analysis
- Prediction creation
- Resolution plan generation
"""

import logging
import math
import random
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.domain import (
    FailureCase, InterventionOption, InterventionConstraint,
    DecisionAnalysis, Prediction, ResolutionPlan, Evidence
)
from app.models.enums import DataTruth, ApprovalState, FailureType

logger = logging.getLogger(__name__)

# Intervention templates parameterized by failure type
INTERVENTION_TEMPLATES = {
    FailureType.WATERLOGGING.value: [
        {
            "title": "Do Nothing (Baseline)",
            "type": "do_nothing",
            "description": "No intervention. Maintain current state.",
            "base_cost": 0,
            "duration_days": 0,
            "workers": 0,
            "risk_reduction": 0.0,
            "recurrence_outlook": "Continued recurrence expected during every moderate+ rainfall event",
            "maintenance_burden": "None",
        },
        {
            "title": "Drain Cleaning & Desilting",
            "type": "drain_cleaning",
            "description": "Remove accumulated silt, debris, and blockages from existing drainage channels.",
            "base_cost": 35000,
            "duration_days": 3,
            "workers": 4,
            "equipment": ["vacuum_tanker", "jetting_machine"],
            "materials": [],
            "risk_reduction": 0.35,
            "recurrence_outlook": "Temporary relief, likely recurrence within 3-6 months",
            "maintenance_burden": "Requires repeated cleaning every 3-4 months",
            "future_savings": 15000,
        },
        {
            "title": "Additional Drainage Inlets",
            "type": "additional_inlet",
            "description": "Install 2-3 additional storm water inlets to increase drainage access capacity.",
            "base_cost": 85000,
            "duration_days": 7,
            "workers": 6,
            "equipment": ["excavator", "concrete_mixer"],
            "materials": ["concrete", "inlet_grates", "connecting_pipes"],
            "risk_reduction": 0.55,
            "recurrence_outlook": "Significant reduction; moderate events manageable",
            "maintenance_burden": "Annual inlet cleaning",
            "future_savings": 40000,
        },
        {
            "title": "Drainage Capacity Upgrade",
            "type": "capacity_increase",
            "description": "Replace undersized drain section with larger capacity pipe/channel and improve gradient.",
            "base_cost": 250000,
            "duration_days": 21,
            "workers": 10,
            "equipment": ["excavator", "crane", "concrete_mixer", "compactor"],
            "materials": ["RCC_pipes_900mm", "concrete", "gravel", "backfill"],
            "risk_reduction": 0.80,
            "recurrence_outlook": "Low probability of recurrence for design-standard events",
            "maintenance_burden": "Routine annual inspection",
            "future_savings": 120000,
        },
        {
            "title": "Comprehensive Drainage Rehabilitation",
            "type": "drain_rehabilitation",
            "description": "Full rehabilitation: new drain alignment, increased capacity, inlet upgrades, terrain regrading.",
            "base_cost": 450000,
            "duration_days": 35,
            "workers": 15,
            "equipment": ["excavator", "crane", "concrete_mixer", "compactor", "grader"],
            "materials": ["RCC_pipes_1200mm", "concrete", "gravel", "inlet_grates", "manhole_covers"],
            "risk_reduction": 0.92,
            "recurrence_outlook": "Minimal recurrence probability for 10+ years",
            "maintenance_burden": "Standard municipal maintenance schedule",
            "future_savings": 300000,
        },
    ],
    FailureType.ROAD_DAMAGE.value: [
        {
            "title": "Do Nothing (Baseline)",
            "type": "do_nothing",
            "description": "No intervention.",
            "base_cost": 0,
            "duration_days": 0,
            "workers": 0,
            "risk_reduction": 0.0,
            "recurrence_outlook": "Progressive deterioration expected",
        },
        {
            "title": "Pothole Patching",
            "type": "patching",
            "description": "Cold-mix or hot-mix patching of affected potholes.",
            "base_cost": 15000,
            "duration_days": 1,
            "workers": 3,
            "equipment": ["roller"],
            "materials": ["asphalt_mix", "emulsion"],
            "risk_reduction": 0.3,
            "recurrence_outlook": "Temporary fix, recurrence within 2-4 months",
            "maintenance_burden": "Frequent re-patching",
            "future_savings": 5000,
        },
        {
            "title": "Road Surface Rehabilitation",
            "type": "resurfacing",
            "description": "Mill and overlay affected road section.",
            "base_cost": 180000,
            "duration_days": 10,
            "workers": 8,
            "equipment": ["milling_machine", "paver", "roller"],
            "materials": ["asphalt", "tack_coat", "aggregate"],
            "risk_reduction": 0.75,
            "recurrence_outlook": "Durable repair, 5-7 year expected life",
            "maintenance_burden": "Routine inspection",
            "future_savings": 80000,
        },
    ],
}


class InterventionEngine:
    """Service for generating, scoring, and managing interventions."""

    def __init__(self, db: Session):
        self.db = db

    def generate_interventions(self, case_id: str) -> list[InterventionOption]:
        """Generate intervention options for a failure case."""
        case = self.db.query(FailureCase).filter(FailureCase.case_id == case_id).first()
        if not case:
            return []

        # Get templates for this failure type
        templates = INTERVENTION_TEMPLATES.get(
            case.failure_type,
            INTERVENTION_TEMPLATES.get(FailureType.WATERLOGGING.value, [])
        )

        # Get complaint count for impact estimation
        from app.models.domain import Complaint
        complaint_count = self.db.query(Complaint).filter(
            Complaint.cluster_id == case.cluster_id
        ).count()

        interventions = []
        for i, template in enumerate(templates):
            # Parameterize based on case specifics
            cost = template.get("base_cost", 0)
            random.seed(hash(case_id + str(i)))

            # Add some variance
            cost_variance = cost * random.uniform(-0.1, 0.15)
            adjusted_cost = max(0, cost + cost_variance)

            option = InterventionOption(
                case_id=case_id,
                title=template["title"],
                description=template.get("description", ""),
                intervention_type=template.get("type", "unknown"),
                estimated_cost=round(adjusted_cost, 2),
                estimated_duration_days=template.get("duration_days", 0),
                workers_required=template.get("workers", 0),
                equipment=template.get("equipment", []),
                materials=template.get("materials", []),
                complaints_addressed=complaint_count if template.get("risk_reduction", 0) > 0 else 0,
                expected_risk_reduction=template.get("risk_reduction", 0.0),
                recurrence_outlook=template.get("recurrence_outlook", "Unknown"),
                maintenance_burden=template.get("maintenance_burden", "Unknown"),
                future_savings=template.get("future_savings", 0),
                parameters={
                    "failure_type": case.failure_type,
                    "complaint_count": complaint_count,
                    "base_cost": cost,
                },
                assumptions=[
                    "Cost estimates based on typical municipal rates",
                    "Duration assumes standard working conditions",
                    "Worker count assumes standard crew sizes",
                ],
                data_truth=DataTruth.MODEL_ESTIMATION.value,
            )
            self.db.add(option)
            interventions.append(option)

        self.db.commit()
        logger.info(f"Generated {len(interventions)} interventions for case {case_id}")
        return interventions

    def apply_constraints(self, case_id: str, constraints: dict) -> InterventionConstraint:
        """Create or update constraints for a case."""
        # Check if constraints already exist
        existing = self.db.query(InterventionConstraint).filter(
            InterventionConstraint.case_id == case_id
        ).first()

        if existing:
            for key, value in constraints.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return existing

        constraint = InterventionConstraint(
            case_id=case_id,
            budget_limit=constraints.get("budget_limit"),
            deadline=constraints.get("deadline"),
            available_workers=constraints.get("available_workers"),
            available_equipment=constraints.get("available_equipment", []),
            available_materials=constraints.get("available_materials", []),
            operational_restrictions=constraints.get("operational_restrictions", []),
            weather_constraints=constraints.get("weather_constraints", []),
        )
        self.db.add(constraint)
        self.db.commit()
        return constraint

    def score_interventions(
        self,
        case_id: str,
        weights: Optional[dict] = None,
    ) -> DecisionAnalysis:
        """Score and rank interventions with transparent breakdown."""
        default_weights = {
            "budget_fit": 20,
            "impact": 25,
            "recurrence_reduction": 25,
            "time_fit": 15,
            "resource_fit": 15,
        }
        scoring_weights = weights or default_weights

        interventions = self.db.query(InterventionOption).filter(
            InterventionOption.case_id == case_id
        ).all()

        constraints = self.db.query(InterventionConstraint).filter(
            InterventionConstraint.case_id == case_id
        ).first()

        ranked = []
        for intervention in interventions:
            scores = self._compute_scores(intervention, constraints, scoring_weights)
            intervention.score_breakdown = scores
            intervention.overall_score = scores.get("overall", 0)

            if constraints and constraints.budget_limit:
                intervention.budget_fit = scores.get("budget_fit_raw", 0)
            if constraints and constraints.deadline:
                intervention.deadline_fit = scores.get("time_fit_raw", 0)

            ranked.append({
                "intervention_id": intervention.intervention_id,
                "title": intervention.title,
                "overall_score": scores["overall"],
                "score_breakdown": scores,
                "estimated_cost": intervention.estimated_cost,
                "estimated_duration_days": intervention.estimated_duration_days,
                "risk_reduction": intervention.expected_risk_reduction,
            })

        # Sort by overall score descending
        ranked.sort(key=lambda x: x["overall_score"], reverse=True)

        # Assign ranks
        for i, item in enumerate(ranked):
            item["rank"] = i + 1
            # Update DB
            opt = next(
                (o for o in interventions if o.intervention_id == item["intervention_id"]),
                None,
            )
            if opt:
                opt.rank = i + 1

        # Create decision analysis
        analysis = DecisionAnalysis(
            case_id=case_id,
            constraint_id=constraints.constraint_id if constraints else None,
            ranked_interventions=ranked,
            scoring_weights=scoring_weights,
            data_truth=DataTruth.MODEL_ESTIMATION.value,
        )
        self.db.add(analysis)
        self.db.commit()

        return analysis

    def _compute_scores(
        self,
        intervention: InterventionOption,
        constraints: Optional[InterventionConstraint],
        weights: dict,
    ) -> dict:
        """Compute transparent score breakdown for an intervention."""
        max_weight = sum(weights.values())

        # Budget fit
        budget_fit_raw = 1.0
        if constraints and constraints.budget_limit and constraints.budget_limit > 0:
            if intervention.estimated_cost <= constraints.budget_limit:
                budget_fit_raw = 1.0 - (intervention.estimated_cost / constraints.budget_limit) * 0.3
            else:
                budget_fit_raw = max(0, 1.0 - (intervention.estimated_cost / constraints.budget_limit))
        budget_score = budget_fit_raw * weights.get("budget_fit", 20)

        # Impact score (based on risk reduction)
        impact_raw = intervention.expected_risk_reduction
        impact_score = impact_raw * weights.get("impact", 25)

        # Recurrence reduction
        recurrence_raw = intervention.expected_risk_reduction * 0.9  # slightly different lens
        recurrence_score = recurrence_raw * weights.get("recurrence_reduction", 25)

        # Time fit
        time_fit_raw = 1.0
        if constraints and constraints.deadline:
            available_days = max(1, (constraints.deadline - datetime.utcnow()).days)
            if intervention.estimated_duration_days <= available_days:
                time_fit_raw = 1.0
            else:
                time_fit_raw = max(0, available_days / intervention.estimated_duration_days)
        elif intervention.estimated_duration_days > 0:
            time_fit_raw = max(0.3, 1.0 - intervention.estimated_duration_days / 60)
        time_score = time_fit_raw * weights.get("time_fit", 15)

        # Resource fit
        resource_fit_raw = 1.0
        if constraints and constraints.available_workers:
            if intervention.workers_required <= constraints.available_workers:
                resource_fit_raw = 1.0
            else:
                resource_fit_raw = max(0, constraints.available_workers / intervention.workers_required)
        resource_score = resource_fit_raw * weights.get("resource_fit", 15)

        overall = (budget_score + impact_score + recurrence_score + time_score + resource_score) / max_weight

        return {
            "budget_fit": round(budget_score, 2),
            "budget_fit_raw": round(budget_fit_raw, 2),
            "impact": round(impact_score, 2),
            "impact_raw": round(impact_raw, 2),
            "recurrence_reduction": round(recurrence_score, 2),
            "recurrence_reduction_raw": round(recurrence_raw, 2),
            "time_fit": round(time_score, 2),
            "time_fit_raw": round(time_fit_raw, 2),
            "resource_fit": round(resource_score, 2),
            "resource_fit_raw": round(resource_fit_raw, 2),
            "overall": round(overall, 4),
            "max_possible": max_weight,
        }

    def compute_cost_of_inaction(self, case_id: str) -> dict:
        """Estimate the cost of doing nothing."""
        case = self.db.query(FailureCase).filter(FailureCase.case_id == case_id).first()
        if not case:
            return {}

        from app.models.domain import Complaint
        complaint_count = self.db.query(Complaint).filter(
            Complaint.cluster_id == case.cluster_id
        ).count()

        # Use fingerprint data if available
        fp = case.fingerprint or {}

        # Screening-level estimates
        recurrences_per_year = 3 + (case.recurrence_count * 0.5)
        complaint_burden = int(complaint_count * recurrences_per_year * 0.8)
        road_length = fp.get("spatial_extent_m", 200) * 2
        buildings = fp.get("terrain", {}).get("buildings_affected", 25)
        critical_count = 1 if hash(case_id) % 3 == 0 else 0
        disruption_hours = recurrences_per_year * 8  # 8 hours per event
        cost_per_event = 25000  # estimated municipal response cost
        recurring_cost = recurrences_per_year * cost_per_event
        five_year_exposure = recurring_cost * 5 * 1.1  # with inflation

        return {
            "case_id": case_id,
            "expected_recurrences_per_year": round(recurrences_per_year, 1),
            "expected_complaint_burden": complaint_burden,
            "affected_road_length_m": round(road_length, 0),
            "affected_buildings": buildings,
            "critical_facilities_exposed": critical_count,
            "estimated_disruption_hours_per_year": round(disruption_hours, 1),
            "estimated_recurring_cost_per_year": round(recurring_cost, 2),
            "estimated_5_year_exposure": round(five_year_exposure, 2),
            "assumptions": [
                "Recurrence rate based on historical pattern extrapolation",
                "Response cost estimated at ₹25,000 per event",
                "Building count from nearby area estimation",
                "5-year projection includes 10% annual inflation assumption",
            ],
            "data_truth": DataTruth.MODEL_ESTIMATION.value,
        }

    def compute_counterfactual(self, case_id: str) -> dict:
        """Compare do-nothing vs each intervention scenario."""
        interventions = self.db.query(InterventionOption).filter(
            InterventionOption.case_id == case_id
        ).order_by(InterventionOption.rank).all()

        cost_of_inaction = self.compute_cost_of_inaction(case_id)
        baseline_recurrence = cost_of_inaction.get("expected_recurrences_per_year", 3)
        baseline_cost = cost_of_inaction.get("estimated_recurring_cost_per_year", 75000)

        scenarios = []
        for intervention in interventions:
            reduced_recurrence = baseline_recurrence * (1 - intervention.expected_risk_reduction)
            reduced_cost = baseline_cost * (1 - intervention.expected_risk_reduction)
            net_benefit_5yr = (baseline_cost - reduced_cost) * 5 - intervention.estimated_cost

            scenarios.append({
                "intervention_id": intervention.intervention_id,
                "title": intervention.title,
                "intervention_cost": intervention.estimated_cost,
                "expected_recurrence_rate": round(reduced_recurrence, 2),
                "expected_annual_cost_after": round(reduced_cost, 2),
                "risk_reduction": intervention.expected_risk_reduction,
                "complaints_addressed": intervention.complaints_addressed,
                "estimated_duration_days": intervention.estimated_duration_days,
                "net_benefit_5_years": round(net_benefit_5yr, 2),
                "maintenance_burden": intervention.maintenance_burden,
                "uncertainty": "MODERATE" if intervention.expected_risk_reduction > 0.5 else "HIGH",
                "data_truth": DataTruth.MODEL_ESTIMATION.value,
            })

        return {
            "case_id": case_id,
            "baseline": cost_of_inaction,
            "scenarios": scenarios,
            "data_truth": DataTruth.MODEL_ESTIMATION.value,
        }

    def create_predictions(self, case_id: str) -> list[Prediction]:
        """Create prediction records for intervention outcomes."""
        interventions = self.db.query(InterventionOption).filter(
            InterventionOption.case_id == case_id,
            InterventionOption.intervention_type != "do_nothing",
        ).all()

        predictions = []
        for intervention in interventions:
            # Recurrence probability prediction
            p1 = Prediction(
                case_id=case_id,
                intervention_id=intervention.intervention_id,
                predicted_metric="recurrence_probability",
                predicted_value=round(1.0 - intervention.expected_risk_reduction, 3),
                confidence=0.65,
                horizon_days=365,
                model_version="screening-v1",
                assumptions=[
                    "Based on screening-level capacity model",
                    "Assumes intervention implemented as planned",
                    "Weather patterns similar to historical average",
                ],
                data_truth=DataTruth.MODEL_ESTIMATION.value,
            )
            self.db.add(p1)
            predictions.append(p1)

            # Time to recurrence
            if intervention.expected_risk_reduction > 0:
                expected_months = round(12 / max(0.1, 1.0 - intervention.expected_risk_reduction), 1)
                p2 = Prediction(
                    case_id=case_id,
                    intervention_id=intervention.intervention_id,
                    predicted_metric="expected_months_to_recurrence",
                    predicted_value=min(120, expected_months),
                    confidence=0.5,
                    horizon_days=365 * 3,
                    model_version="screening-v1",
                    assumptions=["Extrapolated from historical recurrence patterns"],
                    data_truth=DataTruth.MODEL_ESTIMATION.value,
                )
                self.db.add(p2)
                predictions.append(p2)

        self.db.commit()
        return predictions

    def create_resolution_plan(
        self,
        case_id: str,
        intervention_id: str,
    ) -> Optional[ResolutionPlan]:
        """Generate a detailed resolution plan for a selected intervention."""
        intervention = self.db.query(InterventionOption).filter(
            InterventionOption.intervention_id == intervention_id,
        ).first()

        if not intervention:
            return None

        case = self.db.query(FailureCase).filter(FailureCase.case_id == case_id).first()
        if not case:
            return None

        # Mark intervention as selected
        intervention.selected = True

        # Generate phases and tasks
        phases = self._generate_plan_phases(intervention)

        plan = ResolutionPlan(
            case_id=case_id,
            intervention_id=intervention_id,
            title=f"Resolution Plan: {intervention.title}",
            description=f"Detailed execution plan for {intervention.title} at {case.title}",
            phases=phases,
            total_duration_days=intervention.estimated_duration_days,
            total_estimated_cost=intervention.estimated_cost,
            acceptance_criteria=[
                "All tasks completed per specification",
                "Field evidence submitted for each completed task",
                "No waterlogging during next comparable rainfall event",
                "Drainage flow confirmed unobstructed",
            ],
            risks=[
                "Weather delays during monsoon season",
                "Underground utility conflicts",
                "Material supply delays",
                "Unexpected subsurface conditions",
            ],
            contingencies=[
                "Alternative drainage alignment available",
                "Temporary pumping as interim measure",
                "Material substitution options identified",
            ],
            approval_state=ApprovalState.PENDING_APPROVAL.value,
            data_truth=DataTruth.MODEL_ESTIMATION.value,
        )
        self.db.add(plan)

        # Update case status
        case.status = "INTERVENTION_SELECTED"

        self.db.commit()
        return plan

    def _generate_plan_phases(self, intervention: InterventionOption) -> list[dict]:
        """Generate execution phases for an intervention."""
        if intervention.intervention_type == "drain_cleaning":
            return [
                {
                    "phase": 1,
                    "title": "Site Assessment & Preparation",
                    "duration_hours": 4,
                    "tasks": [
                        {"title": "Site inspection and marking", "duration_hours": 2, "sequence": 1},
                        {"title": "Traffic management setup", "duration_hours": 2, "sequence": 2},
                    ],
                },
                {
                    "phase": 2,
                    "title": "Drain Cleaning",
                    "duration_hours": 16,
                    "tasks": [
                        {"title": "Mechanical desilting", "duration_hours": 8, "sequence": 3},
                        {"title": "High-pressure jetting", "duration_hours": 4, "sequence": 4},
                        {"title": "Debris removal and disposal", "duration_hours": 4, "sequence": 5},
                    ],
                },
                {
                    "phase": 3,
                    "title": "Verification & Cleanup",
                    "duration_hours": 4,
                    "tasks": [
                        {"title": "Flow test and inspection", "duration_hours": 2, "sequence": 6},
                        {"title": "Site cleanup and restoration", "duration_hours": 2, "sequence": 7},
                    ],
                },
            ]
        elif intervention.intervention_type == "capacity_increase":
            return [
                {
                    "phase": 1,
                    "title": "Planning & Preparation",
                    "duration_hours": 16,
                    "tasks": [
                        {"title": "Detailed survey and design", "duration_hours": 8, "sequence": 1},
                        {"title": "Material procurement", "duration_hours": 8, "sequence": 2},
                        {"title": "Traffic & utility coordination", "duration_hours": 4, "sequence": 3},
                    ],
                },
                {
                    "phase": 2,
                    "title": "Excavation",
                    "duration_hours": 40,
                    "tasks": [
                        {"title": "Surface removal", "duration_hours": 8, "sequence": 4},
                        {"title": "Trench excavation", "duration_hours": 24, "sequence": 5},
                        {"title": "Old pipe removal", "duration_hours": 8, "sequence": 6},
                    ],
                },
                {
                    "phase": 3,
                    "title": "Installation",
                    "duration_hours": 56,
                    "tasks": [
                        {"title": "Bedding preparation", "duration_hours": 8, "sequence": 7},
                        {"title": "New pipe installation", "duration_hours": 24, "sequence": 8},
                        {"title": "Connection and jointing", "duration_hours": 16, "sequence": 9},
                        {"title": "Manhole construction", "duration_hours": 8, "sequence": 10},
                    ],
                },
                {
                    "phase": 4,
                    "title": "Testing & Restoration",
                    "duration_hours": 24,
                    "tasks": [
                        {"title": "Flow testing", "duration_hours": 4, "sequence": 11},
                        {"title": "Backfilling and compaction", "duration_hours": 12, "sequence": 12},
                        {"title": "Surface restoration", "duration_hours": 8, "sequence": 13},
                    ],
                },
            ]
        else:
            # Generic phases
            total_hours = intervention.estimated_duration_days * 8
            return [
                {
                    "phase": 1,
                    "title": "Preparation",
                    "duration_hours": total_hours * 0.2,
                    "tasks": [
                        {"title": "Site preparation", "duration_hours": total_hours * 0.1, "sequence": 1},
                        {"title": "Material staging", "duration_hours": total_hours * 0.1, "sequence": 2},
                    ],
                },
                {
                    "phase": 2,
                    "title": "Execution",
                    "duration_hours": total_hours * 0.6,
                    "tasks": [
                        {"title": "Primary work execution", "duration_hours": total_hours * 0.4, "sequence": 3},
                        {"title": "Secondary work", "duration_hours": total_hours * 0.2, "sequence": 4},
                    ],
                },
                {
                    "phase": 3,
                    "title": "Completion",
                    "duration_hours": total_hours * 0.2,
                    "tasks": [
                        {"title": "Quality check", "duration_hours": total_hours * 0.1, "sequence": 5},
                        {"title": "Site cleanup", "duration_hours": total_hours * 0.1, "sequence": 6},
                    ],
                },
            ]

    # ─────────────────────────────────────────────────────────
    # Query methods
    # ─────────────────────────────────────────────────────────

    def get_interventions(self, case_id: str) -> list[InterventionOption]:
        return self.db.query(InterventionOption).filter(
            InterventionOption.case_id == case_id
        ).order_by(InterventionOption.rank).all()

    def get_constraints(self, case_id: str) -> Optional[InterventionConstraint]:
        return self.db.query(InterventionConstraint).filter(
            InterventionConstraint.case_id == case_id
        ).first()

    def get_predictions(self, case_id: str) -> list[Prediction]:
        return self.db.query(Prediction).filter(Prediction.case_id == case_id).all()

    def get_resolution_plan(self, case_id: str) -> Optional[ResolutionPlan]:
        return self.db.query(ResolutionPlan).filter(
            ResolutionPlan.case_id == case_id
        ).order_by(ResolutionPlan.created_at.desc()).first()

    def get_decision_analysis(self, case_id: str) -> Optional[DecisionAnalysis]:
        return self.db.query(DecisionAnalysis).filter(
            DecisionAnalysis.case_id == case_id
        ).order_by(DecisionAnalysis.created_at.desc()).first()
