"""
Pydantic schemas for API request/response models.
These map directly to the DATA_CONTRACT.md and API_CONTRACT.md specifications.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# Common
# ─────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None
    field: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    timestamp: datetime


# ─────────────────────────────────────────────────────────────
# CSV Import
# ─────────────────────────────────────────────────────────────

class ImportSummary(BaseModel):
    import_id: str
    filename: str
    status: str
    total_rows: int = 0
    accepted_rows: int = 0
    rejected_rows: int = 0
    duplicate_rows: int = 0
    validation_errors: list = []
    processing_summary: dict = {}
    created_at: datetime
    completed_at: Optional[datetime] = None
    data_truth: str = "REAL_DATA"

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Complaint
# ─────────────────────────────────────────────────────────────

class ComplaintResponse(BaseModel):
    complaint_id: str
    import_id: Optional[str] = None
    title: str
    description: str
    original_text: Optional[str] = None
    incident_type: str
    category: Optional[str] = None
    reported_at: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    ward: Optional[str] = None
    severity: str
    status: str
    source: str
    site_id: Optional[str] = None
    cluster_id: Optional[str] = None
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplaintListResponse(BaseModel):
    complaints: list[ComplaintResponse]
    total: int
    page: int = 1
    page_size: int = 50


# ─────────────────────────────────────────────────────────────
# Site
# ─────────────────────────────────────────────────────────────

class SiteResponse(BaseModel):
    site_id: str
    site_label: str
    latitude: float
    longitude: float
    ward: Optional[str] = None
    neighborhood: Optional[str] = None
    road_segment_id: Optional[str] = None
    h3_cell: Optional[str] = None
    drain_ids: list = []
    building_ids: list = []
    terrain_elevation: Optional[float] = None
    terrain_slope: Optional[float] = None
    land_cover: Optional[str] = None
    data_truth: str

    model_config = {"from_attributes": True}


class SiteContextResponse(BaseModel):
    """Progressive spatial context for a site."""
    site: SiteResponse
    level: str  # SITE, LOCAL, CATCHMENT, CORRIDOR, WARD, CITY
    nearby_complaints: list[ComplaintResponse] = []
    nearby_infrastructure: list[dict] = []
    terrain_context: Optional[dict] = None
    drainage_context: Optional[dict] = None
    building_count: int = 0
    critical_facilities: list[dict] = []
    historical_incidents: list[dict] = []


# ─────────────────────────────────────────────────────────────
# Failure Cluster
# ─────────────────────────────────────────────────────────────

class ClusterResponse(BaseModel):
    cluster_id: str
    title: str
    complaint_count: int
    incident_count: int
    confidence: float
    status: str
    site_id: Optional[str] = None
    centroid_lat: Optional[float] = None
    centroid_lon: Optional[float] = None
    spatial_radius_m: Optional[float] = None
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    categories: list = []
    severity_distribution: dict = {}
    semantic_similarity: Optional[float] = None
    cluster_rationale: Optional[str] = None
    relationship_evidence: dict = {}
    confidence_level: str = "LOW"
    evidence_strength: str = "WEAK"
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ClusterListResponse(BaseModel):
    clusters: list[ClusterResponse]
    total: int


class ClusteringResultResponse(BaseModel):
    total_complaints: int
    total_clusters: int
    unclustered_complaints: int
    clusters: list[ClusterResponse]
    algorithm: str
    parameters: dict


# ─────────────────────────────────────────────────────────────
# Failure Case
# ─────────────────────────────────────────────────────────────

class FailureCaseResponse(BaseModel):
    case_id: str
    cluster_id: str
    site_id: Optional[str] = None
    title: str
    failure_type: str
    recurrence_count: int = 0
    impact_summary: Optional[str] = None
    confidence: float = 0.0
    status: str
    fingerprint: Optional[dict] = None
    failure_chain: Optional[Any] = None
    created_at: datetime
    updated_at: datetime
    data_truth: str

    model_config = {"from_attributes": True}


class FailureCaseListResponse(BaseModel):
    cases: list[FailureCaseResponse]
    total: int


# ─────────────────────────────────────────────────────────────
# Evidence
# ─────────────────────────────────────────────────────────────

class EvidenceResponse(BaseModel):
    evidence_id: str
    case_id: Optional[str] = None
    type: str
    title: str
    source: str
    description: Optional[str] = None
    value: Optional[Any] = None
    confidence: float
    timestamp: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    provenance: Optional[dict] = None
    assumptions: list = []
    limitations: list = []
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EvidenceListResponse(BaseModel):
    evidence: list[EvidenceResponse]
    total: int


# ─────────────────────────────────────────────────────────────
# Failure Hypothesis
# ─────────────────────────────────────────────────────────────

class HypothesisResponse(BaseModel):
    hypothesis_id: str
    case_id: str
    title: str
    description: Optional[str] = None
    confidence: float
    status: str
    evidence_ids: list = []
    mechanism: Optional[str] = None
    assumptions: list = []
    limitations: list = []
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Historical Incident
# ─────────────────────────────────────────────────────────────

class HistoricalIncidentResponse(BaseModel):
    incident_id: str
    case_id: Optional[str] = None
    site_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    incident_type: Optional[str] = None
    occurred_at: datetime
    severity: Optional[str] = None
    intervention_taken: Optional[str] = None
    intervention_outcome: Optional[str] = None
    recurrence_after_days: Optional[int] = None
    data_truth: str

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    case_id: str
    site_id: Optional[str] = None
    historical_incidents: list[HistoricalIncidentResponse] = []
    previous_complaints: list[ComplaintResponse] = []
    recurrence_intervals: list[int] = []
    total_past_incidents: int = 0
    total_previous_interventions: int = 0


# ─────────────────────────────────────────────────────────────
# Reference Case
# ─────────────────────────────────────────────────────────────

class ReferenceCaseResponse(BaseModel):
    reference_id: str
    city: str
    country: Optional[str] = None
    problem_type: str
    intervention: str
    description: Optional[str] = None
    context: Optional[str] = None
    approximate_cost: Optional[float] = None
    cost_currency: str = "INR"
    duration_reported: Optional[str] = None
    reported_outcome: Optional[str] = None
    recurrence_evidence: Optional[str] = None
    source_url: Optional[str] = None
    source_reference: Optional[str] = None
    applicability_notes: Optional[str] = None
    limitations: Optional[str] = None
    confidence: float
    data_truth: str

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Intervention
# ─────────────────────────────────────────────────────────────

class InterventionResponse(BaseModel):
    intervention_id: str
    case_id: str
    title: str
    description: Optional[str] = None
    intervention_type: Optional[str] = None
    estimated_cost: float = 0.0
    estimated_duration_days: float = 0.0
    workers_required: int = 0
    equipment: list = []
    materials: list = []
    complaints_addressed: int = 0
    expected_risk_reduction: float = 0.0
    recurrence_outlook: Optional[str] = None
    maintenance_burden: Optional[str] = None
    future_savings: float = 0.0
    overall_score: float = 0.0
    score_breakdown: dict = {}
    budget_fit: Optional[float] = None
    deadline_fit: Optional[float] = None
    parameters: dict = {}
    assumptions: list = []
    rank: Optional[int] = None
    selected: bool = False
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InterventionListResponse(BaseModel):
    interventions: list[InterventionResponse]
    total: int
    case_id: str


# ─────────────────────────────────────────────────────────────
# Constraint
# ─────────────────────────────────────────────────────────────

class ConstraintRequest(BaseModel):
    budget_limit: Optional[float] = None
    deadline: Optional[datetime] = None
    available_workers: Optional[int] = None
    available_equipment: list = []
    available_materials: list = []
    operational_restrictions: list = []
    weather_constraints: list = []


class ConstraintResponse(BaseModel):
    constraint_id: str
    case_id: str
    budget_limit: Optional[float] = None
    deadline: Optional[datetime] = None
    available_workers: Optional[int] = None
    available_equipment: list = []
    available_materials: list = []
    operational_restrictions: list = []
    weather_constraints: list = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Decision Analysis
# ─────────────────────────────────────────────────────────────

class CostOfInactionResponse(BaseModel):
    case_id: str
    expected_recurrences_per_year: float
    expected_complaint_burden: int
    affected_road_length_m: float
    affected_buildings: int
    critical_facilities_exposed: int
    estimated_disruption_hours_per_year: float
    estimated_recurring_cost_per_year: float
    estimated_5_year_exposure: float
    assumptions: list = []
    data_truth: str = "MODEL_ESTIMATION"


class CounterfactualResponse(BaseModel):
    case_id: str
    scenarios: list[dict]  # Each scenario: intervention + metrics
    data_truth: str = "MODEL_ESTIMATION"


class DecisionAnalysisResponse(BaseModel):
    analysis_id: str
    case_id: str
    ranked_interventions: list[dict]
    scoring_weights: dict
    cost_of_inaction: Optional[dict] = None
    counterfactual: Optional[dict] = None
    selected_intervention_id: Optional[str] = None
    decision_rationale: Optional[str] = None
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Prediction
# ─────────────────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    prediction_id: str
    case_id: str
    intervention_id: Optional[str] = None
    predicted_metric: str
    predicted_value: float
    confidence: float
    horizon_days: Optional[int] = None
    model_version: str
    assumptions: list = []
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CasePredictionResponse(BaseModel):
    case_id: str
    prediction_type: str
    horizon_years: int
    current_risk_score: float
    risk_level: str
    recurrence_probability: float
    expected_incidents: dict
    expected_complaints: dict
    exposure_level: str
    yearly_projection: list = []
    evidence_basis: list = []
    uncertainties: list = []
    methodology: str
    data_origin: str

    model_config = {"from_attributes": True}


class SimulationRequest(BaseModel):
    intervention_id: Optional[str] = None
    budget: Optional[float] = None
    deadline_days: Optional[int] = None
    workers: Optional[int] = None
    excavators: Optional[int] = None
    road_disruption_tolerance: Optional[str] = None
    maintenance_capacity: Optional[str] = None


class SimulationResponse(BaseModel):
    baseline: dict
    intervention: Optional[dict] = None
    feasibility: str
    risk_before: float
    risk_after: float
    risk_reduction: float
    recurrence_before: dict
    recurrence_after: dict
    complaint_burden_before: dict
    complaint_burden_after: dict
    cost: float
    duration: int
    resources: dict
    maintenance: str
    confidence: float
    score: float
    reasons: list = []
    limitations: list = []

    model_config = {"from_attributes": True}

class SimulationRunResponse(BaseModel):
    simulation_id: str
    case_id: str
    site_id: Optional[str] = None
    intervention_id: Optional[str] = None
    constraints: dict = {}
    baseline_snapshot: dict = {}
    result: dict = {}
    score: Optional[float] = None
    feasibility: Optional[str] = None
    created_at: datetime
    data_origin: str

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Resolution Plan
# ─────────────────────────────────────────────────────────────

class ResolutionPlanResponse(BaseModel):
    plan_id: str
    case_id: str
    intervention_id: str
    title: str
    description: Optional[str] = None
    phases: list = []
    total_duration_days: float
    total_estimated_cost: float
    acceptance_criteria: list = []
    risks: list = []
    contingencies: list = []
    approval_state: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalRequest(BaseModel):
    approved_by: str
    decision: str  # "APPROVED" or "REJECTED"
    notes: Optional[str] = None


# ─────────────────────────────────────────────────────────────
# Work Order
# ─────────────────────────────────────────────────────────────

class WorkOrderResponse(BaseModel):
    work_order_id: str
    plan_id: Optional[str] = None
    intervention_id: str
    case_id: str
    title: str
    description: Optional[str] = None
    status: str
    approval_state: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    task_id: str
    work_order_id: str
    title: str
    description: Optional[str] = None
    sequence: int
    status: str
    planned_duration_hours: float
    actual_duration_hours: Optional[float] = None
    workers: list = []
    equipment: list = []
    materials: list = []
    dependencies: list = []
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    completion_percentage: float = 0.0
    notes: Optional[str] = None
    delay_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskUpdateRequest(BaseModel):
    status: Optional[str] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    completion_percentage: Optional[float] = None
    notes: Optional[str] = None
    delay_reason: Optional[str] = None
    actual_duration_hours: Optional[float] = None


class TaskDelayResponse(BaseModel):
    task: TaskResponse
    replan_event: "ReplanEventResponse"

    model_config = {"from_attributes": True}


class ExecutionEventResponse(BaseModel):
    event_id: str
    work_order_id: str
    task_id: Optional[str] = None
    event_type: str
    description: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class ReplanEventResponse(BaseModel):
    replan_id: str
    work_order_id: str
    reason: str
    trigger_event_id: Optional[str] = None
    previous_plan: Optional[dict] = None
    new_plan: Optional[dict] = None
    affected_tasks: list = []
    deadline_risk: Optional[str] = None
    recommended_actions: list = []
    requires_human_approval: bool = True
    approved: Optional[bool] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Field Evidence
# ─────────────────────────────────────────────────────────────

class FieldEvidenceResponse(BaseModel):
    evidence_id: str
    work_order_id: str
    task_id: Optional[str] = None
    evidence_type: str
    captured_at: datetime
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    metadata_info: dict = {}
    location_consistency: Optional[str] = None
    timestamp_consistency: Optional[str] = None
    duplicate_similarity: Optional[float] = None
    visual_change: Optional[str] = None
    manipulation_indicators: list = []
    overall_consistency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FieldEvidenceRequest(BaseModel):
    work_order_id: str
    task_id: Optional[str] = None
    evidence_type: str = "PHOTO"
    captured_at: datetime
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    metadata_info: dict = {}


# ─────────────────────────────────────────────────────────────
# Verification
# ─────────────────────────────────────────────────────────────

class VerificationResponse(BaseModel):
    verification_id: str
    work_order_id: str
    status: str
    overall_consistency: str
    checks: list = []
    evidence_ids: list = []
    confidence: float
    manual_review_required: bool
    review_reason: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Outcome
# ─────────────────────────────────────────────────────────────

class OutcomeRequest(BaseModel):
    case_id: str
    work_order_id: Optional[str] = None
    observed_at: datetime
    status: str  # IMPROVED, UNCHANGED, RECURRENCE, INCONCLUSIVE
    trigger_event: Optional[str] = None
    trigger_event_details: Optional[dict] = None
    observed_conditions: Optional[dict] = None
    complaints_during_event: int = 0
    spatial_impact: Optional[dict] = None
    notes: Optional[str] = None


class OutcomeResponse(BaseModel):
    outcome_id: str
    case_id: str
    work_order_id: Optional[str] = None
    observed_at: datetime
    status: str
    trigger_event: Optional[str] = None
    trigger_event_details: Optional[dict] = None
    observed_conditions: Optional[dict] = None
    complaints_during_event: int
    spatial_impact: Optional[dict] = None
    notes: Optional[str] = None
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Prediction vs Reality
# ─────────────────────────────────────────────────────────────

class PredictionRealityResponse(BaseModel):
    comparison_id: str
    prediction_id: str
    outcome_id: str
    case_id: str
    predicted_value: float
    observed_value: Optional[float] = None
    predicted_metric: str
    comparison_result: str
    error: Optional[float] = None
    error_percentage: Optional[float] = None
    model_version: Optional[str] = None
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Learning
# ─────────────────────────────────────────────────────────────

class LearningRecordResponse(BaseModel):
    learning_id: str
    case_id: str
    site_id: Optional[str] = None
    comparison_id: Optional[str] = None
    learning_type: str
    title: str
    description: Optional[str] = None
    previous_confidence: Optional[float] = None
    updated_confidence: Optional[float] = None
    intervention_type: Optional[str] = None
    effectiveness_rating: Optional[float] = None
    recommendations: list = []
    evidence_ids: list = []
    data_truth: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Infrastructure Memory
# ─────────────────────────────────────────────────────────────

class InfrastructureMemoryResponse(BaseModel):
    memory_id: str
    site_id: str
    title: str
    summary: Optional[str] = None
    timeline: list = []
    total_complaints: int = 0
    total_cases: int = 0
    total_interventions: int = 0
    total_recurrences: int = 0
    successful_interventions: list = []
    failed_interventions: list = []
    learned_patterns: list = []
    last_incident_at: Optional[datetime] = None
    last_intervention_at: Optional[datetime] = None
    recurrence_intervals: list = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# City Overview
# ─────────────────────────────────────────────────────────────

class CityOverviewResponse(BaseModel):
    total_complaints: int
    total_clusters: int
    total_failure_cases: int
    total_active_work_orders: int
    total_verified: int
    total_outcomes: int
    complaints_by_ward: dict = {}
    complaints_by_severity: dict = {}
    complaints_by_category: dict = {}
    clusters_by_status: dict = {}
    recent_complaints: list[ComplaintResponse] = []
    active_cases: list[FailureCaseResponse] = []


# ─────────────────────────────────────────────────────────────
# Map
# ─────────────────────────────────────────────────────────────

class MapFeature(BaseModel):
    id: str
    type: str  # complaint, cluster, site, work_order
    latitude: float
    longitude: float
    properties: dict = {}


class MapDataResponse(BaseModel):
    features: list[MapFeature]
    total: int
    bounds: Optional[dict] = None  # {min_lat, max_lat, min_lon, max_lon}


# ─────────────────────────────────────────────────────────────
# Complete Case View
# ─────────────────────────────────────────────────────────────

class CaseCompleteResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    case: FailureCaseResponse
    cluster: ClusterResponse
    site: Optional[SiteResponse] = None
    complaints: list[ComplaintResponse] = []
    evidence: list[EvidenceResponse] = []
    failure_hypothesis: list[HypothesisResponse] = []
    history: Optional[HistoryResponse] = None
    prediction: Optional[CasePredictionResponse] = None
    predictions: list[PredictionResponse] = []
    approach_research: list[ReferenceCaseResponse] = []
    constraints: Optional[ConstraintResponse] = None
    interventions: list[InterventionResponse] = []
    simulation_runs: list[dict] = []
    officer_feedback: list[dict] = []
    decision: Optional[DecisionAnalysisResponse] = None
    roadmap: Optional[ResolutionPlanResponse] = None
    work_order: Optional[WorkOrderResponse] = None
    tasks: list[TaskResponse] = []
    field_evidence: list[FieldEvidenceResponse] = []
    verification: Optional[VerificationResponse] = None
    outcome: Optional[OutcomeResponse] = None
    memory: Optional[InfrastructureMemoryResponse] = None

