# CIVIC PULSE — DATA CONTRACT

Version: 1.0
Status: ACTIVE

This document defines the shared data model.

The purpose is to prevent backend and frontend from creating different meanings for the same object.

---

# 1. CORE ENTITY CHAIN

Complaint
→ Site
→ Failure Cluster
→ Case
→ Evidence
→ Hypothesis
→ Intervention
→ Work Order
→ Task
→ Verification
→ Outcome
→ Memory

---

# 2. COMPLAINT

Required:

complaint_id
title
description
incident_type
reported_at
site_id
severity
source
data_truth

Optional:

cluster_id
latitude
longitude
address
attachments

---

# 3. SITE

A Site is a stable physical location.

Required:

site_id
latitude
longitude
site_label

Optional:

road_segment_id
h3_cell
ward
neighborhood
drain_ids
building_ids

The Site ID should remain stable even when complaint geocoding varies slightly.

---

# 4. FAILURE CLUSTER

Required:

cluster_id
title
complaint_count
incident_count
confidence
site_id
status

Must maintain:

member complaint IDs

Never lose the relationship between a cluster and its complaints.

---

# 5. CASE

A Case represents an investigated infrastructure failure.

Required:

case_id
cluster_id
site_id
title
failure_type
status
created_at

Optional:

fingerprint
history
failure_chain
decision_readiness
selected_intervention
outcome

---

# 6. FAILURE HYPOTHESIS

Required:

hypothesis_id
case_id
title
confidence
status

Must include evidence IDs.

Example:

{
  "hypothesis_id": "HYP-001",
  "title": "Drainage capacity constraint",
  "confidence": 0.86,
  "evidence_ids": ["EV-001", "EV-004"]
}

---

# 7. EVIDENCE

Required:

evidence_id
case_id
type
title
source
confidence
data_truth

Possible types:

COMPLAINT
RAINFALL
TERRAIN
DRAINAGE
ROAD
SATELLITE
FIELD_PHOTO
HISTORICAL_INCIDENT
WORK_ORDER
OUTCOME
CROSS_CITY_CASE

---

# 8. DATA TRUTH

Every record should use one of:

REAL_DATA
SYNTHETIC_DATA
MODEL_ESTIMATION
AI_GENERATED_TEXT
EVIDENCE
ASSUMPTION

For mixed records, separate the components instead of falsely assigning one label to everything.

---

# 9. INTERVENTION

Required:

intervention_id
case_id
title
description
estimated_cost
estimated_duration_days
workers_required
overall_score

Optional:

equipment
materials
complaints_addressed
expected_risk_reduction
recurrence_outlook
budget_fit
deadline_fit
maintenance_burden
future_savings

---

# 10. INTERVENTION SCORE

Scores must be explainable.

Store individual components.

Example:

{
  "impact_score": 0.82,
  "budget_fit": 0.94,
  "deadline_fit": 0.90,
  "evidence_confidence": 0.84,
  "recurrence_reduction": 0.72,
  "overall_score": 0.82
}

Do not store only one unexplained score.

---

# 11. CONSTRAINTS

Constraints are first-class data.

Possible:

budget_limit
deadline
available_workers
available_equipment
available_materials
operational_restrictions
weather_constraints

Example:

{
  "budget_limit": 150000,
  "deadline": "2026-10-15",
  "available_workers": 8,
  "available_equipment": [
    "vacuum_tanker"
  ]
}

---

# 12. WORK ORDER

Required:

work_order_id
intervention_id
status
approval_state
created_at

Approval states:

DRAFT
PENDING_APPROVAL
APPROVED
REJECTED
CANCELLED

---

# 13. TASK

Required:

task_id
work_order_id
title
sequence
status
planned_duration_hours

Optional:

actual_duration_hours
workers
equipment
materials
dependencies
planned_start
planned_end
actual_start
actual_end
notes

---

# 14. EXECUTION EVENTS

Execution changes must be recorded.

Examples:

TASK_STARTED
TASK_COMPLETED
TASK_DELAYED
RESOURCE_CHANGED
TASK_BLOCKED
PLAN_REVISED
APPROVAL_GRANTED

Do not overwrite history when something changes.

---

# 15. REPLAN

Required:

replan_id
work_order_id
reason
created_at
requires_human_approval

Optional:

previous_plan
new_plan
deadline_risk
recommended_actions

---

# 16. FIELD EVIDENCE

Required:

evidence_id
work_order_id
task_id
captured_at
latitude
longitude

Optional:

image_url
metadata
visual_change
duplicate_similarity
location_consistency
timestamp_consistency
manipulation_indicators

---

# 17. VERIFICATION

Required:

verification_id
work_order_id
status
overall_consistency

Possible statuses:

VERIFIED
REVIEW_REQUIRED
REJECTED

Verification must NOT automatically mean problem resolution.

---

# 18. OUTCOME

Required:

outcome_id
case_id
observed_at
status

Possible:

IMPROVED
UNCHANGED
RECURRENCE
INCONCLUSIVE

Must preserve:

predicted outcome
observed outcome

---

# 19. PREDICTION VS REALITY

Store both.

Example:

{
  "prediction": {
    "recurrence_probability": 0.18
  },
  "observed": {
    "recurrence": false
  },
  "comparison": "MATCHED"
}

Possible comparisons:

MATCHED
PARTIALLY_MATCHED
MISMATCHED
INCONCLUSIVE

---

# 20. MEMORY

Memory connects long-term location history.

Required:

memory_id
site_id

Contains:

cases
interventions
outcomes
recurrence
learned_patterns

---

# 21. RELATIONSHIP INTEGRITY

Every relationship must be explicit.

Examples:

complaint.cluster_id
complaint.site_id

cluster.case_id

case.site_id

case.evidence_ids

hypothesis.evidence_ids

intervention.case_id

work_order.intervention_id

task.work_order_id

verification.work_order_id

outcome.case_id

memory.site_id

---

# 22. PROVENANCE

Important values should contain provenance where possible.

Example:

{
  "value": 42,
  "source": "OpenStreetMap",
  "retrieved_at": "...",
  "data_truth": "REAL_DATA"
}

---

# 23. ASSUMPTIONS

Any assumption must be explicit.

Example:

{
  "parameter": "cost_per_disruption_hour",
  "value": 500,
  "data_truth": "ASSUMPTION"
}

Do not hide assumptions inside calculations.

---

# 24. SYNTHETIC DATA

Synthetic demo data is allowed.

However:

- label it SYNTHETIC_DATA
- keep it reproducible
- maintain realistic relationships
- do not present it as PMC data
- do not fabricate official government records

Real open datasets can be combined with synthetic complaints/history/work orders.

---

# 25. FRONTEND DATA RULE

Frontend must not create alternative field names.

If backend says:

complaint_count

frontend must use:

complaint_count

Not:

complaints
count
totalComplaints

unless explicitly defined by the contract.

---

# 26. BACKEND DATA RULE

Backend must not return undocumented fields as required frontend behavior.

Optional fields must be clearly marked.

---

# 27. DATA EVOLUTION

If a field changes:

1. update DATA_CONTRACT.md
2. update backend model/schema
3. update API contract
4. update frontend type
5. update mocks
6. update tests

---

# 28. SOURCE OF TRUTH

Backend database/schema is the source of truth for persisted data.

API_CONTRACT.md is the source of truth for communication.

DATA_CONTRACT.md is the source of truth for entity meaning.

ARCHITECTURE.md is the source of truth for product behavior.

Frontend must never become the source of truth for backend data.