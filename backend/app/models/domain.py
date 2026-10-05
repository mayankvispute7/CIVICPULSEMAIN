"""
Complete domain models for Civic Pulse.

Implements the full entity chain:
Complaint → Site → FailureCluster → FailureCase → Evidence → Hypothesis
→ Intervention → WorkOrder → Task → ExecutionEvent → Verification
→ Outcome → PredictionReality → Learning → InfrastructureMemory
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum as SAEnum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.enums import (
    DataTruth, Severity, ComplaintStatus, ClusterStatus, CaseStatus,
    EvidenceType, HypothesisStatus, ApprovalState, WorkOrderStatus,
    TaskStatus, ExecutionEventType, VerificationStatus, EvidenceConsistency,
    OutcomeStatus, PredictionComparison, ImportStatus, FailureType
)


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────
# CSV Import
# ─────────────────────────────────────────────────────────────

class CSVImport(Base):
    __tablename__ = "csv_imports"

    import_id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    status = Column(String, default=ImportStatus.PENDING.value, nullable=False)
    total_rows = Column(Integer, default=0)
    accepted_rows = Column(Integer, default=0)
    rejected_rows = Column(Integer, default=0)
    duplicate_rows = Column(Integer, default=0)
    validation_errors = Column(JSON, default=list)
    processing_summary = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    data_truth = Column(String, default=DataTruth.REAL_DATA.value)

    complaints = relationship("Complaint", back_populates="csv_import")


# ─────────────────────────────────────────────────────────────
# Site
# ─────────────────────────────────────────────────────────────

class Site(Base):
    __tablename__ = "sites"

    site_id = Column(String, primary_key=True, default=generate_uuid)
    site_label = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    ward = Column(String, nullable=True)
    neighborhood = Column(String, nullable=True)
    road_segment_id = Column(String, nullable=True)
    h3_cell = Column(String, nullable=True)
    drain_ids = Column(JSON, default=list)
    building_ids = Column(JSON, default=list)
    terrain_elevation = Column(Float, nullable=True)
    terrain_slope = Column(Float, nullable=True)
    land_cover = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    data_truth = Column(String, default=DataTruth.SYNTHETIC_DATA.value)

    complaints = relationship("Complaint", back_populates="site")
    failure_clusters = relationship("FailureCluster", back_populates="site")
    failure_cases = relationship("FailureCase", back_populates="site")
    memories = relationship("InfrastructureMemory", back_populates="site")


# ─────────────────────────────────────────────────────────────
# Complaint
# ─────────────────────────────────────────────────────────────

class Complaint(Base):
    __tablename__ = "complaints"

    complaint_id = Column(String, primary_key=True, default=generate_uuid)
    import_id = Column(String, ForeignKey("csv_imports.import_id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    original_text = Column(Text, nullable=True)  # preserve original
    incident_type = Column(String, nullable=False)
    category = Column(String, nullable=True)
    reported_at = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    original_address = Column(String, nullable=True)
    ward = Column(String, nullable=True)
    severity = Column(String, default=Severity.MEDIUM.value)
    status = Column(String, default=ComplaintStatus.NEW.value)
    source = Column(String, default="CSV")

    site_id = Column(String, ForeignKey("sites.site_id"), nullable=True)
    cluster_id = Column(String, ForeignKey("failure_clusters.cluster_id"), nullable=True)

    data_truth = Column(String, default=DataTruth.REAL_DATA.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    normalized_at = Column(DateTime, nullable=True)

    csv_import = relationship("CSVImport", back_populates="complaints")
    site = relationship("Site", back_populates="complaints")
    cluster = relationship("FailureCluster", back_populates="complaints")

    __table_args__ = (
        Index("idx_complaint_location", "latitude", "longitude"),
        Index("idx_complaint_cluster", "cluster_id"),
        Index("idx_complaint_site", "site_id"),
        Index("idx_complaint_reported_at", "reported_at"),
        Index("idx_complaint_ward", "ward"),
    )


# ─────────────────────────────────────────────────────────────
# Failure Cluster
# ─────────────────────────────────────────────────────────────

class FailureCluster(Base):
    __tablename__ = "failure_clusters"

    cluster_id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    complaint_count = Column(Integer, default=0)
    incident_count = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    status = Column(String, default=ClusterStatus.DRAFT.value)

    site_id = Column(String, ForeignKey("sites.site_id"), nullable=True)
    centroid_lat = Column(Float, nullable=True)
    centroid_lon = Column(Float, nullable=True)
    spatial_radius_m = Column(Float, nullable=True)
    time_range_start = Column(DateTime, nullable=True)
    time_range_end = Column(DateTime, nullable=True)
    categories = Column(JSON, default=list)
    severity_distribution = Column(JSON, default=dict)
    semantic_similarity = Column(Float, nullable=True)
    cluster_rationale = Column(Text, nullable=True)
    relationship_evidence = Column(JSON, default=dict)
    confidence_level = Column(String, default="LOW")
    evidence_strength = Column(String, default="WEAK")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_truth = Column(String, default=DataTruth.MODEL_ESTIMATION.value)

    site = relationship("Site", back_populates="failure_clusters")
    complaints = relationship("Complaint", back_populates="cluster")
    failure_cases = relationship("FailureCase", back_populates="cluster")


# ─────────────────────────────────────────────────────────────
# Failure Case
# ─────────────────────────────────────────────────────────────

class FailureCase(Base):
    __tablename__ = "failure_cases"

    case_id = Column(String, primary_key=True, default=generate_uuid)
    cluster_id = Column(String, ForeignKey("failure_clusters.cluster_id"), nullable=False)
    site_id = Column(String, ForeignKey("sites.site_id"), nullable=True)
    title = Column(String, nullable=False)
    failure_type = Column(String, default=FailureType.OTHER.value)
    recurrence_count = Column(Integer, default=0)
    impact_summary = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    status = Column(String, default=CaseStatus.OPEN.value)

    # Failure fingerprint (embedded)
    fingerprint = Column(JSON, nullable=True)
    failure_chain = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_truth = Column(String, default=DataTruth.MODEL_ESTIMATION.value)

    cluster = relationship("FailureCluster", back_populates="failure_cases")
    site = relationship("Site", back_populates="failure_cases")
    evidence_items = relationship("Evidence", back_populates="failure_case")
    hypotheses = relationship("FailureHypothesis", back_populates="failure_case")
    interventions = relationship("InterventionOption", back_populates="failure_case")
    predictions = relationship("Prediction", back_populates="failure_case")
    outcomes = relationship("OutcomeObservation", back_populates="failure_case")
    historical_incidents = relationship("HistoricalIncident", back_populates="failure_case")


# ─────────────────────────────────────────────────────────────
# Evidence
# ─────────────────────────────────────────────────────────────

class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=True)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    value = Column(JSON, nullable=True)
    confidence = Column(Float, default=0.5)
    timestamp = Column(DateTime, nullable=True)
    date_range_start = Column(DateTime, nullable=True)
    date_range_end = Column(DateTime, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    provenance = Column(JSON, nullable=True)
    assumptions = Column(JSON, default=list)
    limitations = Column(JSON, default=list)
    data_truth = Column(String, default=DataTruth.EVIDENCE.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    failure_case = relationship("FailureCase", back_populates="evidence_items")


# ─────────────────────────────────────────────────────────────
# Failure Hypothesis
# ─────────────────────────────────────────────────────────────

class FailureHypothesis(Base):
    __tablename__ = "failure_hypotheses"

    hypothesis_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    status = Column(String, default=HypothesisStatus.PROPOSED.value)
    evidence_ids = Column(JSON, default=list)
    mechanism = Column(Text, nullable=True)
    assumptions = Column(JSON, default=list)
    limitations = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_truth = Column(String, default=DataTruth.MODEL_ESTIMATION.value)

    failure_case = relationship("FailureCase", back_populates="hypotheses")


# ─────────────────────────────────────────────────────────────
# Historical Incident
# ─────────────────────────────────────────────────────────────

class HistoricalIncident(Base):
    __tablename__ = "historical_incidents"

    incident_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=True)
    site_id = Column(String, ForeignKey("sites.site_id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    incident_type = Column(String, nullable=True)
    occurred_at = Column(DateTime, nullable=False)
    severity = Column(String, nullable=True)
    intervention_taken = Column(String, nullable=True)
    intervention_outcome = Column(String, nullable=True)
    recurrence_after_days = Column(Integer, nullable=True)
    evidence_ids = Column(JSON, default=list)
    data_truth = Column(String, default=DataTruth.SYNTHETIC_DATA.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    failure_case = relationship("FailureCase", back_populates="historical_incidents")


# ─────────────────────────────────────────────────────────────
# Cross-City Reference Case
# ─────────────────────────────────────────────────────────────

class ReferenceCaseLibrary(Base):
    __tablename__ = "reference_cases"

    reference_id = Column(String, primary_key=True, default=generate_uuid)
    city = Column(String, nullable=False)
    country = Column(String, nullable=True)
    problem_type = Column(String, nullable=False)
    intervention = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    context = Column(Text, nullable=True)
    approximate_cost = Column(Float, nullable=True)
    cost_currency = Column(String, default="INR")
    duration_reported = Column(String, nullable=True)
    reported_outcome = Column(String, nullable=True)
    recurrence_evidence = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    source_reference = Column(String, nullable=True)
    applicability_notes = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    confidence = Column(Float, default=0.5)
    date_added = Column(DateTime, default=datetime.utcnow)
    data_truth = Column(String, default=DataTruth.EVIDENCE.value)


# ─────────────────────────────────────────────────────────────
# Intervention Option
# ─────────────────────────────────────────────────────────────

class InterventionOption(Base):
    __tablename__ = "intervention_options"

    intervention_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    intervention_type = Column(String, nullable=True)

    # Cost & resources
    estimated_cost = Column(Float, default=0.0)
    estimated_duration_days = Column(Float, default=0.0)
    workers_required = Column(Integer, default=0)
    equipment = Column(JSON, default=list)
    materials = Column(JSON, default=list)

    # Impact estimates
    complaints_addressed = Column(Integer, default=0)
    expected_risk_reduction = Column(Float, default=0.0)
    recurrence_outlook = Column(String, nullable=True)
    maintenance_burden = Column(String, nullable=True)
    future_savings = Column(Float, default=0.0)

    # Scoring
    overall_score = Column(Float, default=0.0)
    score_breakdown = Column(JSON, default=dict)
    budget_fit = Column(Float, nullable=True)
    deadline_fit = Column(Float, nullable=True)

    # Parameters for screening-level model
    parameters = Column(JSON, default=dict)
    assumptions = Column(JSON, default=list)

    rank = Column(Integer, nullable=True)
    selected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    data_truth = Column(String, default=DataTruth.MODEL_ESTIMATION.value)

    failure_case = relationship("FailureCase", back_populates="interventions")
    work_orders = relationship("WorkOrder", back_populates="intervention")


# ─────────────────────────────────────────────────────────────
# Intervention Constraint
# ─────────────────────────────────────────────────────────────

class InterventionConstraint(Base):
    __tablename__ = "intervention_constraints"

    constraint_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    budget_limit = Column(Float, nullable=True)
    deadline = Column(DateTime, nullable=True)
    available_workers = Column(Integer, nullable=True)
    available_equipment = Column(JSON, default=list)
    available_materials = Column(JSON, default=list)
    operational_restrictions = Column(JSON, default=list)
    weather_constraints = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─────────────────────────────────────────────────────────────
# Decision Analysis
# ─────────────────────────────────────────────────────────────

class DecisionAnalysis(Base):
    __tablename__ = "decision_analyses"

    analysis_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    constraint_id = Column(String, ForeignKey("intervention_constraints.constraint_id"), nullable=True)
    ranked_interventions = Column(JSON, default=list)
    scoring_weights = Column(JSON, default=dict)
    cost_of_inaction = Column(JSON, nullable=True)
    counterfactual = Column(JSON, nullable=True)
    selected_intervention_id = Column(String, nullable=True)
    decision_rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    data_truth = Column(String, default=DataTruth.MODEL_ESTIMATION.value)


# ─────────────────────────────────────────────────────────────
# Prediction
# ─────────────────────────────────────────────────────────────

class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    intervention_id = Column(String, ForeignKey("intervention_options.intervention_id"), nullable=True)
    predicted_metric = Column(String, nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence = Column(Float, default=0.5)
    horizon_days = Column(Integer, nullable=True)
    model_version = Column(String, default="screening-v1")
    assumptions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    data_truth = Column(String, default=DataTruth.MODEL_ESTIMATION.value)

    failure_case = relationship("FailureCase", back_populates="predictions")


# ─────────────────────────────────────────────────────────────
# Resolution Plan
# ─────────────────────────────────────────────────────────────

class ResolutionPlan(Base):
    __tablename__ = "resolution_plans"

    plan_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    intervention_id = Column(String, ForeignKey("intervention_options.intervention_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    phases = Column(JSON, default=list)
    total_duration_days = Column(Float, default=0.0)
    total_estimated_cost = Column(Float, default=0.0)
    acceptance_criteria = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    contingencies = Column(JSON, default=list)
    approval_state = Column(String, default=ApprovalState.DRAFT.value)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_truth = Column(String, default=DataTruth.MODEL_ESTIMATION.value)


# ─────────────────────────────────────────────────────────────
# Work Order
# ─────────────────────────────────────────────────────────────

class WorkOrder(Base):
    __tablename__ = "work_orders"

    work_order_id = Column(String, primary_key=True, default=generate_uuid)
    plan_id = Column(String, ForeignKey("resolution_plans.plan_id"), nullable=True)
    intervention_id = Column(String, ForeignKey("intervention_options.intervention_id"), nullable=False)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default=WorkOrderStatus.DRAFT.value)
    approval_state = Column(String, default=ApprovalState.DRAFT.value)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    planned_start = Column(DateTime, nullable=True)
    planned_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    intervention = relationship("InterventionOption", back_populates="work_orders")
    tasks = relationship("WorkOrderTask", back_populates="work_order")
    execution_events = relationship("ExecutionEvent", back_populates="work_order")
    replan_events = relationship("ReplanEvent", back_populates="work_order")
    field_evidence = relationship("FieldEvidence", back_populates="work_order")
    verifications = relationship("Verification", back_populates="work_order")


# ─────────────────────────────────────────────────────────────
# Work Order Task
# ─────────────────────────────────────────────────────────────

class WorkOrderTask(Base):
    __tablename__ = "work_order_tasks"

    task_id = Column(String, primary_key=True, default=generate_uuid)
    work_order_id = Column(String, ForeignKey("work_orders.work_order_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    sequence = Column(Integer, default=0)
    status = Column(String, default=TaskStatus.PENDING.value)
    planned_duration_hours = Column(Float, default=0.0)
    actual_duration_hours = Column(Float, nullable=True)
    workers = Column(JSON, default=list)
    equipment = Column(JSON, default=list)
    materials = Column(JSON, default=list)
    dependencies = Column(JSON, default=list)  # list of task_ids
    planned_start = Column(DateTime, nullable=True)
    planned_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    completion_percentage = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    delay_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="tasks")


# ─────────────────────────────────────────────────────────────
# Execution Event
# ─────────────────────────────────────────────────────────────

class ExecutionEvent(Base):
    __tablename__ = "execution_events"

    event_id = Column(String, primary_key=True, default=generate_uuid)
    work_order_id = Column(String, ForeignKey("work_orders.work_order_id"), nullable=False)
    task_id = Column(String, ForeignKey("work_order_tasks.task_id"), nullable=True)
    event_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="execution_events")


# ─────────────────────────────────────────────────────────────
# Replan Event
# ─────────────────────────────────────────────────────────────

class ReplanEvent(Base):
    __tablename__ = "replan_events"

    replan_id = Column(String, primary_key=True, default=generate_uuid)
    work_order_id = Column(String, ForeignKey("work_orders.work_order_id"), nullable=False)
    reason = Column(Text, nullable=False)
    trigger_event_id = Column(String, nullable=True)
    previous_plan = Column(JSON, nullable=True)
    new_plan = Column(JSON, nullable=True)
    affected_tasks = Column(JSON, default=list)
    deadline_risk = Column(String, nullable=True)
    recommended_actions = Column(JSON, default=list)
    requires_human_approval = Column(Boolean, default=True)
    approved = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="replan_events")


# ─────────────────────────────────────────────────────────────
# Field Evidence
# ─────────────────────────────────────────────────────────────

class FieldEvidence(Base):
    __tablename__ = "field_evidence"

    evidence_id = Column(String, primary_key=True, default=generate_uuid)
    work_order_id = Column(String, ForeignKey("work_orders.work_order_id"), nullable=False)
    task_id = Column(String, ForeignKey("work_order_tasks.task_id"), nullable=True)
    evidence_type = Column(String, default="PHOTO")
    captured_at = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    metadata_info = Column(JSON, default=dict)

    # Integrity checks
    location_consistency = Column(String, nullable=True)
    timestamp_consistency = Column(String, nullable=True)
    duplicate_similarity = Column(Float, nullable=True)
    visual_change = Column(String, nullable=True)
    manipulation_indicators = Column(JSON, default=list)
    overall_consistency = Column(String, default=EvidenceConsistency.MEDIUM.value)

    created_at = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="field_evidence")


# ─────────────────────────────────────────────────────────────
# Verification
# ─────────────────────────────────────────────────────────────

class Verification(Base):
    __tablename__ = "verifications"

    verification_id = Column(String, primary_key=True, default=generate_uuid)
    work_order_id = Column(String, ForeignKey("work_orders.work_order_id"), nullable=False)
    status = Column(String, default=VerificationStatus.PENDING.value)
    overall_consistency = Column(String, default=EvidenceConsistency.MEDIUM.value)
    checks = Column(JSON, default=list)
    evidence_ids = Column(JSON, default=list)
    confidence = Column(Float, default=0.0)
    manual_review_required = Column(Boolean, default=False)
    review_reason = Column(Text, nullable=True)
    verified_by = Column(String, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="verifications")


# ─────────────────────────────────────────────────────────────
# Outcome Observation
# ─────────────────────────────────────────────────────────────

class OutcomeObservation(Base):
    __tablename__ = "outcome_observations"

    outcome_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    work_order_id = Column(String, ForeignKey("work_orders.work_order_id"), nullable=True)
    observed_at = Column(DateTime, nullable=False)
    status = Column(String, default=OutcomeStatus.INCONCLUSIVE.value)
    trigger_event = Column(String, nullable=True)  # e.g., "Heavy rainfall on 2026-09-15"
    trigger_event_details = Column(JSON, nullable=True)
    observed_conditions = Column(JSON, nullable=True)
    complaints_during_event = Column(Integer, default=0)
    spatial_impact = Column(JSON, nullable=True)
    verification_evidence_ids = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    data_truth = Column(String, default=DataTruth.EVIDENCE.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    failure_case = relationship("FailureCase", back_populates="outcomes")


# ─────────────────────────────────────────────────────────────
# Prediction vs Reality
# ─────────────────────────────────────────────────────────────

class PredictionRealityComparison(Base):
    __tablename__ = "prediction_reality_comparisons"

    comparison_id = Column(String, primary_key=True, default=generate_uuid)
    prediction_id = Column(String, ForeignKey("predictions.prediction_id"), nullable=False)
    outcome_id = Column(String, ForeignKey("outcome_observations.outcome_id"), nullable=False)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    predicted_value = Column(Float, nullable=False)
    observed_value = Column(Float, nullable=True)
    predicted_metric = Column(String, nullable=False)
    comparison_result = Column(String, default=PredictionComparison.INCONCLUSIVE.value)
    error = Column(Float, nullable=True)
    error_percentage = Column(Float, nullable=True)
    model_version = Column(String, nullable=True)
    comparison_date = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, default=0.5)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────────────────────
# Learning Record
# ─────────────────────────────────────────────────────────────

class LearningRecord(Base):
    __tablename__ = "learning_records"

    learning_id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("failure_cases.case_id"), nullable=False)
    site_id = Column(String, ForeignKey("sites.site_id"), nullable=True)
    comparison_id = Column(String, ForeignKey("prediction_reality_comparisons.comparison_id"), nullable=True)
    learning_type = Column(String, nullable=False)  # e.g., "intervention_effectiveness"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    previous_confidence = Column(Float, nullable=True)
    updated_confidence = Column(Float, nullable=True)
    intervention_type = Column(String, nullable=True)
    effectiveness_rating = Column(Float, nullable=True)
    recommendations = Column(JSON, default=list)
    evidence_ids = Column(JSON, default=list)
    data_truth = Column(String, default=DataTruth.MODEL_ESTIMATION.value)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────────────────────
# Infrastructure Memory
# ─────────────────────────────────────────────────────────────

class InfrastructureMemory(Base):
    __tablename__ = "infrastructure_memory"

    memory_id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.site_id"), nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    timeline = Column(JSON, default=list)  # ordered events
    total_complaints = Column(Integer, default=0)
    total_cases = Column(Integer, default=0)
    total_interventions = Column(Integer, default=0)
    total_recurrences = Column(Integer, default=0)
    successful_interventions = Column(JSON, default=list)
    failed_interventions = Column(JSON, default=list)
    learned_patterns = Column(JSON, default=list)
    last_incident_at = Column(DateTime, nullable=True)
    last_intervention_at = Column(DateTime, nullable=True)
    recurrence_intervals = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    site = relationship("Site", back_populates="memories")
