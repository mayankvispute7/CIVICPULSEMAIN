export interface ErrorResponse {
  code: string;
  message: string;
  details?: any;
  field?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  timestamp: string;
}

// ─────────────────────────────────────────────────────────────
// CSV Import
// ─────────────────────────────────────────────────────────────

export interface ImportSummary {
  import_id: string;
  filename: string;
  status: string;
  total_rows: number;
  accepted_rows: number;
  rejected_rows: number;
  duplicate_rows: number;
  validation_errors: any[];
  processing_summary: Record<string, any>;
  created_at: string;
  completed_at?: string;
  data_truth: string;
}

// ─────────────────────────────────────────────────────────────
// Complaint
// ─────────────────────────────────────────────────────────────

export interface ComplaintResponse {
  complaint_id: string;
  import_id?: string;
  title: string;
  description: string;
  original_text?: string;
  incident_type: string;
  category?: string;
  reported_at: string;
  latitude?: number;
  longitude?: number;
  address?: string;
  ward?: string;
  severity: string;
  status: string;
  source: string;
  site_id?: string;
  cluster_id?: string;
  data_truth: string;
  created_at: string;
}

export interface ComplaintListResponse {
  complaints: ComplaintResponse[];
  total: number;
  page: number;
  page_size: number;
}

// ─────────────────────────────────────────────────────────────
// Site
// ─────────────────────────────────────────────────────────────

export interface SiteResponse {
  site_id: string;
  site_label: string;
  latitude: number;
  longitude: number;
  ward?: string;
  neighborhood?: string;
  road_segment_id?: string;
  h3_cell?: string;
  drain_ids: any[];
  building_ids: any[];
  terrain_elevation?: number;
  terrain_slope?: number;
  land_cover?: string;
  data_truth: string;
}

export interface SiteContextResponse {
  site: SiteResponse;
  level: string; // SITE, LOCAL, CATCHMENT, CORRIDOR, WARD, CITY
  nearby_complaints: ComplaintResponse[];
  nearby_infrastructure: any[];
  terrain_context?: Record<string, any>;
  drainage_context?: Record<string, any>;
  building_count: number;
  critical_facilities: any[];
  historical_incidents: any[];
}

// ─────────────────────────────────────────────────────────────
// Failure Cluster
// ─────────────────────────────────────────────────────────────

export interface ClusterResponse {
  cluster_id: string;
  title: string;
  complaint_count: number;
  incident_count: number;
  confidence: number;
  status: string;
  site_id?: string;
  centroid_lat?: number;
  centroid_lon?: number;
  spatial_radius_m?: number;
  time_range_start?: string;
  time_range_end?: string;
  categories: any[];
  severity_distribution: Record<string, any>;
  semantic_similarity?: number;
  cluster_rationale?: string;
  data_truth: string;
  created_at: string;
}

export interface ClusterListResponse {
  clusters: ClusterResponse[];
  total: number;
}

export interface ClusteringResultResponse {
  total_complaints: number;
  total_clusters: number;
  unclustered_complaints: number;
  clusters: ClusterResponse[];
  algorithm: string;
  parameters: Record<string, any>;
}

// ─────────────────────────────────────────────────────────────
// Failure Case
// ─────────────────────────────────────────────────────────────

export interface FailureCaseResponse {
  case_id: string;
  cluster_id: string;
  site_id?: string;
  title: string;
  failure_type: string;
  recurrence_count: number;
  impact_summary?: string;
  confidence: number;
  status: string;
  fingerprint?: Record<string, any>;
  failure_chain?: any[];
  created_at: string;
  updated_at: string;
  data_truth: string;
}

export interface FailureCaseListResponse {
  cases: FailureCaseResponse[];
  total: number;
}

// ─────────────────────────────────────────────────────────────
// Evidence
// ─────────────────────────────────────────────────────────────

export interface EvidenceResponse {
  evidence_id: string;
  case_id?: string;
  type: string;
  title: string;
  source: string;
  description?: string;
  value?: any;
  confidence: number;
  timestamp?: string;
  latitude?: number;
  longitude?: number;
  provenance?: Record<string, any>;
  assumptions: any[];
  limitations: any[];
  data_truth: string;
  created_at: string;
}

export interface EvidenceListResponse {
  evidence: EvidenceResponse[];
  total: number;
}

// ─────────────────────────────────────────────────────────────
// Failure Hypothesis
// ─────────────────────────────────────────────────────────────

export interface HypothesisResponse {
  hypothesis_id: string;
  case_id: string;
  title: string;
  description?: string;
  confidence: number;
  status: string;
  evidence_ids: any[];
  mechanism?: string;
  assumptions: any[];
  limitations: any[];
  data_truth: string;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Historical Incident
// ─────────────────────────────────────────────────────────────

export interface HistoricalIncidentResponse {
  incident_id: string;
  case_id?: string;
  site_id?: string;
  title: string;
  description?: string;
  incident_type?: string;
  occurred_at: string;
  severity?: string;
  intervention_taken?: string;
  intervention_outcome?: string;
  recurrence_after_days?: number;
  data_truth: string;
}

export interface HistoryResponse {
  case_id: string;
  site_id?: string;
  historical_incidents: HistoricalIncidentResponse[];
  previous_complaints: ComplaintResponse[];
  recurrence_intervals: number[];
  total_past_incidents: number;
  total_previous_interventions: number;
}

// ─────────────────────────────────────────────────────────────
// Reference Case
// ─────────────────────────────────────────────────────────────

export interface ReferenceCaseResponse {
  reference_id: string;
  city: string;
  country?: string;
  problem_type: string;
  intervention: string;
  description?: string;
  context?: string;
  approximate_cost?: number;
  cost_currency: string;
  duration_reported?: string;
  reported_outcome?: string;
  recurrence_evidence?: string;
  source_url?: string;
  source_reference?: string;
  applicability_notes?: string;
  limitations?: string;
  confidence: number;
  data_truth: string;
}

// ─────────────────────────────────────────────────────────────
// Intervention
// ─────────────────────────────────────────────────────────────

export interface InterventionResponse {
  intervention_id: string;
  case_id: string;
  title: string;
  description?: string;
  intervention_type?: string;
  estimated_cost: number;
  estimated_duration_days: number;
  workers_required: number;
  equipment: any[];
  materials: any[];
  complaints_addressed: number;
  expected_risk_reduction: number;
  recurrence_outlook?: string;
  maintenance_burden?: string;
  future_savings: number;
  overall_score: number;
  score_breakdown: Record<string, any>;
  budget_fit?: number;
  deadline_fit?: number;
  parameters: Record<string, any>;
  assumptions: any[];
  rank?: number;
  selected: boolean;
  data_truth: string;
  created_at: string;
}

export interface InterventionListResponse {
  interventions: InterventionResponse[];
  total: number;
  case_id: string;
}

// ─────────────────────────────────────────────────────────────
// Constraint
// ─────────────────────────────────────────────────────────────

export interface ConstraintRequest {
  budget_limit?: number;
  deadline?: string;
  available_workers?: number;
  available_equipment: any[];
  available_materials: any[];
  operational_restrictions: any[];
  weather_constraints: any[];
}

export interface ConstraintResponse {
  constraint_id: string;
  case_id: string;
  budget_limit?: number;
  deadline?: string;
  available_workers?: number;
  available_equipment: any[];
  available_materials: any[];
  operational_restrictions: any[];
  weather_constraints: any[];
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Decision Analysis
// ─────────────────────────────────────────────────────────────

export interface CostOfInactionResponse {
  case_id: string;
  expected_recurrences_per_year: number;
  expected_complaint_burden: number;
  affected_road_length_m: number;
  affected_buildings: number;
  critical_facilities_exposed: number;
  estimated_disruption_hours_per_year: number;
  estimated_recurring_cost_per_year: number;
  estimated_5_year_exposure: number;
  assumptions: any[];
  data_truth: string;
}

export interface CounterfactualResponse {
  case_id: string;
  scenarios: Record<string, any>[];
  data_truth: string;
}

export interface DecisionAnalysisResponse {
  analysis_id: string;
  case_id: string;
  ranked_interventions: Record<string, any>[];
  scoring_weights: Record<string, any>;
  cost_of_inaction?: Record<string, any>;
  counterfactual?: Record<string, any>;
  selected_intervention_id?: string;
  decision_rationale?: string;
  data_truth: string;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Prediction
// ─────────────────────────────────────────────────────────────

export interface PredictionResponse {
  prediction_id: string;
  case_id: string;
  intervention_id?: string;
  predicted_metric: string;
  predicted_value: number;
  confidence: number;
  horizon_days?: number;
  model_version: string;
  assumptions: any[];
  data_truth: string;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Resolution Plan
// ─────────────────────────────────────────────────────────────

export interface ResolutionPlanResponse {
  plan_id: string;
  case_id: string;
  intervention_id: string;
  title: string;
  description?: string;
  phases: any[];
  total_duration_days: number;
  total_estimated_cost: number;
  acceptance_criteria: any[];
  risks: any[];
  contingencies: any[];
  approval_state: string;
  approved_by?: string;
  approved_at?: string;
  data_truth: string;
  created_at: string;
}

export interface ApprovalRequest {
  approved_by: string;
  decision: string; // "APPROVED" or "REJECTED"
  notes?: string;
}

// ─────────────────────────────────────────────────────────────
// Work Order
// ─────────────────────────────────────────────────────────────

export interface WorkOrderResponse {
  work_order_id: string;
  plan_id?: string;
  intervention_id: string;
  case_id: string;
  title: string;
  description?: string;
  status: string;
  approval_state: string;
  approved_by?: string;
  approved_at?: string;
  planned_start?: string;
  planned_end?: string;
  actual_start?: string;
  actual_end?: string;
  location_lat?: number;
  location_lon?: number;
  created_at: string;
}

export interface TaskResponse {
  task_id: string;
  work_order_id: string;
  title: string;
  description?: string;
  sequence: number;
  status: string;
  planned_duration_hours: number;
  actual_duration_hours?: number;
  workers: any[];
  equipment: any[];
  materials: any[];
  dependencies: any[];
  planned_start?: string;
  planned_end?: string;
  actual_start?: string;
  actual_end?: string;
  completion_percentage: number;
  notes?: string;
  delay_reason?: string;
  created_at: string;
}

export interface TaskUpdateRequest {
  status?: string;
  actual_start?: string;
  actual_end?: string;
  completion_percentage?: number;
  notes?: string;
  delay_reason?: string;
  actual_duration_hours?: number;
}

export interface ExecutionEventResponse {
  event_id: string;
  work_order_id: string;
  task_id?: string;
  event_type: string;
  description?: string;
  old_value?: any;
  new_value?: any;
  timestamp: string;
}

export interface ReplanEventResponse {
  replan_id: string;
  work_order_id: string;
  reason: string;
  trigger_event_id?: string;
  previous_plan?: Record<string, any>;
  new_plan?: Record<string, any>;
  affected_tasks: any[];
  deadline_risk?: string;
  recommended_actions: any[];
  requires_human_approval: boolean;
  approved?: boolean;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Field Evidence
// ─────────────────────────────────────────────────────────────

export interface FieldEvidenceResponse {
  evidence_id: string;
  work_order_id: string;
  task_id?: string;
  evidence_type: string;
  captured_at: string;
  latitude: number;
  longitude: number;
  image_url?: string;
  metadata_info: Record<string, any>;
  location_consistency?: string;
  timestamp_consistency?: string;
  duplicate_similarity?: number;
  visual_change?: string;
  manipulation_indicators: any[];
  overall_consistency: string;
  created_at: string;
}

export interface FieldEvidenceRequest {
  work_order_id: string;
  task_id?: string;
  evidence_type?: string;
  captured_at: string;
  latitude: number;
  longitude: number;
  image_url?: string;
  metadata_info: Record<string, any>;
}

// ─────────────────────────────────────────────────────────────
// Verification
// ─────────────────────────────────────────────────────────────

export interface VerificationResponse {
  verification_id: string;
  work_order_id: string;
  status: string;
  overall_consistency: string;
  checks: any[];
  evidence_ids: any[];
  confidence: number;
  manual_review_required: boolean;
  review_reason?: string;
  verified_by?: string;
  verified_at?: string;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Outcome
// ─────────────────────────────────────────────────────────────

export interface OutcomeRequest {
  case_id: string;
  work_order_id?: string;
  observed_at: string;
  status: string; // IMPROVED, UNCHANGED, RECURRENCE, INCONCLUSIVE
  trigger_event?: string;
  trigger_event_details?: Record<string, any>;
  observed_conditions?: Record<string, any>;
  complaints_during_event?: number;
  spatial_impact?: Record<string, any>;
  notes?: string;
}

export interface OutcomeResponse {
  outcome_id: string;
  case_id: string;
  work_order_id?: string;
  observed_at: string;
  status: string;
  trigger_event?: string;
  trigger_event_details?: Record<string, any>;
  observed_conditions?: Record<string, any>;
  complaints_during_event: number;
  spatial_impact?: Record<string, any>;
  notes?: string;
  data_truth: string;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Prediction vs Reality
// ─────────────────────────────────────────────────────────────

export interface PredictionRealityResponse {
  comparison_id: string;
  prediction_id: string;
  outcome_id: string;
  case_id: string;
  predicted_value: number;
  observed_value?: number;
  predicted_metric: string;
  comparison_result: string;
  error?: number;
  error_percentage?: number;
  model_version?: string;
  confidence: number;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Learning
// ─────────────────────────────────────────────────────────────

export interface LearningRecordResponse {
  learning_id: string;
  case_id: string;
  site_id?: string;
  comparison_id?: string;
  learning_type: string;
  title: string;
  description?: string;
  previous_confidence?: number;
  updated_confidence?: number;
  intervention_type?: string;
  effectiveness_rating?: number;
  recommendations: any[];
  evidence_ids: any[];
  data_truth: string;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Infrastructure Memory
// ─────────────────────────────────────────────────────────────

export interface InfrastructureMemoryResponse {
  memory_id: string;
  site_id: string;
  title: string;
  summary?: string;
  timeline: any[];
  total_complaints: number;
  total_cases: number;
  total_interventions: number;
  total_recurrences: number;
  successful_interventions: any[];
  failed_interventions: any[];
  learned_patterns: any[];
  last_incident_at?: string;
  last_intervention_at?: string;
  recurrence_intervals: number[];
  created_at: string;
  updated_at: string;
}

// ─────────────────────────────────────────────────────────────
// City Overview
// ─────────────────────────────────────────────────────────────

export interface CityOverviewResponse {
  total_complaints: number;
  total_clusters: number;
  total_failure_cases: number;
  total_active_work_orders: number;
  total_verified: number;
  total_outcomes: number;
  complaints_by_ward: Record<string, any>;
  complaints_by_severity: Record<string, any>;
  complaints_by_category: Record<string, any>;
  clusters_by_status: Record<string, any>;
  recent_complaints: ComplaintResponse[];
  active_cases: FailureCaseResponse[];
}

// ─────────────────────────────────────────────────────────────
// Map
// ─────────────────────────────────────────────────────────────

export interface MapFeature {
  id: string;
  type: string; // complaint, cluster, site, work_order
  latitude: number;
  longitude: number;
  properties: Record<string, any>;
}

export interface MapDataResponse {
  features: MapFeature[];
  total: number;
  bounds?: Record<string, any>; // {min_lat, max_lat, min_lon, max_lon}
}

// ─────────────────────────────────────────────────────────────
// Complete Case View
// ─────────────────────────────────────────────────────────────

export interface CaseCompleteResponse {
  case: FailureCaseResponse;
  cluster: ClusterResponse;
  site?: SiteResponse;
  complaints: ComplaintResponse[];
  evidence: EvidenceResponse[];
  failure_hypothesis: HypothesisResponse[];
  history?: HistoryResponse;
  predictions: PredictionResponse[];
  approach_research: ReferenceCaseResponse[];
  constraints?: ConstraintResponse;
  interventions: InterventionResponse[];
  simulation_runs: any[];
  officer_feedback: any[];
  decision?: DecisionAnalysisResponse;
  roadmap?: ResolutionPlanResponse;
  work_order?: WorkOrderResponse;
  tasks: TaskResponse[];
  field_evidence: FieldEvidenceResponse[];
  verification?: VerificationResponse;
  outcome?: OutcomeResponse;
  memory?: InfrastructureMemoryResponse;
}
