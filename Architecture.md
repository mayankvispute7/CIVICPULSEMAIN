# CIVIC PULSE — SYSTEM ARCHITECTURE

Version: 1.0
Status: ACTIVE
Project: Civic Pulse
Tagline: From Infrastructure Failure to Verified Resolution

---

## 1. PRODUCT DEFINITION

Civic Pulse is an infrastructure failure intelligence platform.

It is NOT primarily a complaint-management application.

Existing civic systems can receive complaints, assign them, track work orders and close cases.

Civic Pulse operates above that workflow.

Its purpose is to determine:

1. What complaints are actually related?
2. Which complaints are symptoms of the same underlying infrastructure failure?
3. Why is the failure happening?
4. Has this happened before?
5. What interventions are feasible?
6. What happens if each intervention is selected?
7. Which intervention provides the best expected outcome under real constraints?
8. How should the intervention be executed?
9. Was the work actually completed?
10. Did the physical problem improve?
11. Did reality match the prediction?
12. What should the system remember for the next incident?

Core lifecycle:

COMPLAINT
→ EXTRACTION
→ GEOLOCATION
→ CLUSTERING
→ FAILURE CASE
→ INVESTIGATION
→ HISTORY
→ FAILURE FINGERPRINT
→ DECISION READINESS
→ INTERVENTION EXPLORATION
→ COUNTERFACTUAL ANALYSIS
→ PREDICTION
→ RESOLUTION PLAN
→ WORK ORDER
→ EXECUTION
→ VERIFICATION
→ OUTCOME
→ PREDICTION VS REALITY
→ LEARNING
→ INFRASTRUCTURE MEMORY

Then:

NEXT INCIDENT
→ MEMORY REUSED

---

# 2. CORE PRODUCT PRINCIPLE

Complexity belongs in the system, not in the user's face.

The user interface should remain simple.

The backend may perform:

- spatial analysis
- clustering
- historical analysis
- evidence fusion
- rainfall correlation
- terrain analysis
- intervention scoring
- counterfactual calculations
- constraint optimization
- execution monitoring
- verification
- outcome comparison
- learning

But the officer should see understandable conclusions and supporting evidence.

---

# 3. PRIMARY PRODUCT QUESTIONS

Each major screen must answer one primary question.

Command Center:
"What is happening?"

Intake:
"What complaints came in?"

Clustering:
"Which complaints are actually the same failure?"

Case:
"Why is this happening?"

History:
"Has this happened before?"

Evidence:
"What evidence supports this conclusion?"

Intervention Lab:
"What can we do?"

Counterfactual:
"What happens if we do or do not intervene?"

Decision:
"Which option is most suitable?"

Execution:
"What needs to happen now?"

Verification:
"Was the work actually completed?"

Outcome:
"Did the problem actually improve?"

Memory:
"What have we learned about this place?"

---

# 4. SYSTEM LAYERS

## Layer 1 — Intake

Inputs:

- complaint PDFs
- complaint CSV/JSON
- structured reports
- field reports
- field photographs
- future municipal APIs

Output:

Normalized Complaint objects.

---

## Layer 2 — Geospatial Intelligence

Convert complaint descriptions into spatial entities.

Tasks:

- address extraction
- locality extraction
- road extraction
- coordinates
- geocoding
- spatial normalization
- road snapping
- H3/site assignment

Output:

Complaint + stable spatial identity.

---

## Layer 3 — Complaint Clustering

Determine whether multiple complaints are symptoms of the same failure.

Use:

- spatial proximity
- temporal proximity
- semantic similarity
- incident type
- rainfall relationship
- infrastructure relationship

Possible algorithms:

- DBSCAN
- HDBSCAN
- embeddings
- hybrid scoring

Do NOT blindly merge complaints.

Every cluster must have:

- cluster ID
- member complaint IDs
- clustering confidence
- reasons for grouping
- unresolved/ambiguous cases where appropriate

---

## Layer 4 — Failure Case

A failure cluster becomes a structured Case.

Example:

Case:
FP-2026-007

Title:
Recurring Waterlogging — FC Road Corridor

Contains:

- complaints
- incidents
- location
- affected roads
- infrastructure
- rainfall
- terrain
- drainage
- historical events
- evidence
- previous interventions
- root-cause hypotheses

---

# 5. FAILURE FINGERPRINT

A Failure Fingerprint summarizes the characteristics of a recurring failure.

Example:

Recurring waterlogging

18 complaints
4 historical incidents
86% hypothesis confidence

Evidence suggests:

- terrain accumulation
- drainage capacity/connectivity constraint
- repeated post-rain recurrence

Evidence must be traceable.

Do NOT state:

"AI proved the drain is broken."

Use:

"Evidence suggests a drainage capacity/connectivity constraint combined with local terrain accumulation."

---

# 6. FAILURE CHAIN

Represent the suspected mechanism.

Example:

Heavy Rainfall
↓
High Runoff
↓
Terrain Depression
↓
Drainage Bottleneck
↓
Water Accumulation
↓
Road Disruption
↓
Multiple Complaints

Each node should be backed by evidence where possible.

This is an evidence-based failure mechanism hypothesis.

Do not claim strict causal proof unless the underlying model supports it.

---

# 7. INFRASTRUCTURE GRAPH

The system may represent relationships between:

- sites
- roads
- drains
- complaints
- incidents
- rainfall events
- terrain
- buildings
- critical facilities
- interventions
- work orders
- field evidence
- verification events
- outcomes

Example relationships:

complaint → near → road

complaint → belongs_to → failure_cluster

failure_cluster → associated_with → drain

failure_cluster → correlated_with → rainfall_event

intervention → targets → infrastructure

work_order → implements → intervention

verification → verifies → work_order

outcome → measures → failure_cluster

Use PostgreSQL/PostGIS relationships first.

Do NOT introduce Neo4j unless technically necessary.

---

# 8. POINT → LOCATION INTELLIGENCE

Selecting one complaint or case must expose progressively larger context.

Level 1 — Site Context

Approx. 50m:

- selected complaint
- nearest road
- nearest drain/inlet
- site characteristics

Level 2 — Local Context

Approx. 250m:

- nearby complaints
- failure cluster
- buildings
- critical facilities
- roads

Level 3 — Catchment Context

- terrain
- drainage direction
- runoff context
- land cover
- drainage network

Level 4 — Corridor Context

Approximately 1km along relevant road/corridor.

Level 5 — Neighborhood/Ward Context

Aggregated incident and recurrence statistics.

Do not show everything simultaneously.

Use progressive disclosure.

---

# 9. HISTORY / TIME MACHINE

For every important site or failure case, retrieve historical information.

Show:

- previous complaints
- previous incidents
- previous interventions
- previous work orders
- previous verification
- recurrence interval
- previous hypotheses
- previous outcomes

Question:

"Has this happened before, and what happened last time?"

---

# 10. CROSS-CITY CASE LIBRARY

The system may contain a curated library of approaches used in other cities/regions.

Each case should include:

- location
- problem
- intervention
- approximate cost if known
- implementation conditions
- reported outcome
- recurrence evidence if available
- source/reference
- applicability notes

This is SUPPORTING EVIDENCE.

Do not automatically claim:

"This intervention will work in Pune."

Instead:

"Similar intervention observed elsewhere. Applicability requires local validation."

---

# 11. INTERVENTION LAB

The system must NOT be limited to three hardcoded scenarios.

Possible intervention parameters may include:

- drain cleaning
- desilting
- additional inlet
- capacity increase
- maintenance frequency
- local regrading
- flow diversion
- infrastructure replacement
- localized drainage upgrade
- combined interventions

Each option must be represented as structured data.

For each option calculate/estimate:

- estimated cost
- duration
- workers
- equipment
- material requirements
- affected complaints
- expected risk reduction
- recurrence outlook
- maintenance burden
- deadline feasibility
- budget feasibility
- expected avoided recurring cost

All estimates must be labelled as estimates.

---

# 12. SCREENING-LEVEL HYDRAULIC MODEL

Where appropriate, use a screening-level physical model.

Possible components:

Demand:

- rainfall
- catchment area
- runoff coefficient

Capacity:

- drainage dimensions
- estimated capacity
- blockage factor

Intervention:

- blockage reduction
- capacity increase
- additional inlet
- regrading
- diversion

Output:

- capacity/exceedance ratio
- expected recurrence
- relative risk reduction
- affected area

Label:

"Screening-level estimate. Not calibrated against flood-depth observations."

Parameters marked ASSUMPTION must remain visible.

Do not claim full hydraulic simulation unless a calibrated hydraulic model is actually implemented.

---

# 13. COST OF INACTION

Estimate exposure, not guaranteed damage.

Possible inputs:

- historical recurrence
- affected road length
- buildings in affected area
- critical facilities
- population proxies
- disruption duration
- maintenance burden

Outputs:

- expected recurring incidents
- exposure
- estimated recurring cost
- potential avoided cost

All financial assumptions must be editable and labelled ASSUMPTION.

Never present modelled exposure as measured economic damage.

---

# 14. DECISION ENGINE

Every intervention should receive a transparent score.

Possible factors:

- budget fit
- workforce fit
- deadline fit
- cost
- expected benefit
- complaints addressed
- recurrence reduction
- duration
- maintenance burden
- future savings
- evidence confidence

Example:

Overall Score =
weighted combination of:

Impact
+
Feasibility
+
Evidence Confidence
+
Recurrence Reduction
+
Economic Value

The exact weights must be configurable.

Never hide the reasoning behind the ranking.

---

# 15. EXECUTION ENGINE

A selected intervention becomes an execution plan.

Each task should include:

- task ID
- work order ID
- worker/team
- equipment
- materials
- location
- dependencies
- planned start
- planned duration
- deadline
- status

Statuses:

PENDING
IN_PROGRESS
BLOCKED
COMPLETED
SKIPPED
ESCALATED

---

# 16. DYNAMIC REPLANNING

The plan must respond to execution changes.

Example:

Expected pump arrival:
2 hours

Actual delay:
4 hours

System should recalculate:

- remaining schedule
- deadline risk
- dependent tasks
- alternative resources
- mitigation options

If the selected approach becomes infeasible, show alternate feasible options.

Do not silently change the approved intervention.

Human approval remains required for material changes.

---

# 17. FIELD EVIDENCE INTEGRITY

Field evidence should be checked for:

- GPS consistency
- timestamp
- work-order location
- duplicate/reused image
- visual change
- same-place consistency
- metadata consistency
- possible manipulation indicators

Do NOT claim that an AI detector can reliably prove an image is fake.

Output example:

Evidence consistency:
HIGH

or:

Evidence consistency:
LOW — manual verification required.

Possible actions:

ACCEPT
REQUEST RECAPTURE
ESCALATE

---

# 18. EARTH OBSERVATION

Satellite/remote sensing is SUPPORTING evidence.

Potential sources:

- Sentinel-1
- Sentinel-2
- DEM
- land-cover datasets

Use it for:

- environmental context
- wet-area/change signals
- land-cover context
- terrain context
- spatial change evidence

Do NOT claim:

"Satellite proves contractor completed the work."

Use:

"Independent spatial evidence supports/does not support the reported change."

---

# 19. OUTCOME VERIFICATION

Verification is not the same as work completion.

The system must distinguish:

WORK COMPLETED

from:

PROBLEM RESOLVED

After intervention:

1. verify execution
2. observe next comparable event
3. compare outcome
4. update case

Example:

Predicted recurrence:
low

Next rainfall event:
occurred

Observed recurrence:
none

Prediction:
MATCHED

---

# 20. LEARNING

After each completed case:

Compare:

PREDICTION
vs
REALITY

Update:

- intervention effectiveness
- recurrence estimates
- hypothesis confidence
- cost assumptions
- planning assumptions
- similar-case recommendations

Do not automatically rewrite historical records.

Create new outcome observations.

---

# 21. INFRASTRUCTURE MEMORY

The final system should maintain a persistent history:

Site
→ Complaints
→ Failure Clusters
→ Hypotheses
→ Interventions
→ Work Orders
→ Verification
→ Outcomes

When the same location has a future incident, retrieve this memory.

Example:

"This location experienced 4 similar incidents in the previous 24 months."

"Previous intervention: drain cleaning."

"Recurrence observed after 3 months."

"Previous intervention therefore had limited durability."

This is one of the core differentiators of Civic Pulse.

---

# 22. DATA TRUTH LABELS

Every important value must be classified as one of:

REAL DATA
SYNTHETIC DATA
MODEL ESTIMATION
AI-GENERATED TEXT
EVIDENCE
ASSUMPTION

The UI should make this distinction visible where relevant.

Never present synthetic demo data as real municipal data.

---

# 23. AI PRINCIPLE

Use AI where language or pattern recognition requires it.

Prefer deterministic methods for:

- geospatial calculations
- scoring
- spatial relationships
- physical calculations
- schedules
- work-order states
- evidence lineage

LLMs may be used for:

- complaint extraction
- summarization
- evidence explanation
- decision briefs
- investigation assistance

LLMs must NOT invent evidence.

---

# 24. HUMAN APPROVAL

Human approval is required before:

- issuing a work order
- changing an approved intervention
- accepting low-confidence evidence
- declaring a case resolved
- making high-impact operational decisions

Civic Pulse is decision support, not autonomous government.

---

# 25. DATABASE

Preferred:

PostgreSQL
+
PostGIS

Optional:

pgvector

Do not introduce:

Neo4j
separate vector database
Redis
Kafka
Kubernetes

unless a demonstrated technical requirement exists.

Keep the MVP reliable.

---

# 26. SHARED CONTRACT RULE

The following documents are mandatory:

ARCHITECTURE.md
API_CONTRACT.md
DATA_CONTRACT.md
INTEGRATION_CHECKLIST.md

If a developer discovers a requirement that is not documented:

DO NOT silently invent it.

First update the appropriate contract/document.

Then implement it.

---

# 27. NO UNDOCUMENTED CONNECTIONS

Every major entity must have stable IDs.

Examples:

complaint_id
cluster_id
case_id
site_id
evidence_id
intervention_id
work_order_id
task_id
verification_id
outcome_id
memory_id

Relationships must use these IDs.

Never rely on display names as identifiers.

---

# 28. DEVELOPMENT RULE

Backend and frontend are developed independently.

Backend owns:

/backend

Frontend owns:

/frontend

Both follow:

ARCHITECTURE.md
API_CONTRACT.md
DATA_CONTRACT.md
INTEGRATION_CHECKLIST.md

Final merge should be an integration pass, NOT a rebuild.