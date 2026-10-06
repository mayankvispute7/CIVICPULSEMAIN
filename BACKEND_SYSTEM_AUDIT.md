# BACKEND SYSTEM AUDIT

## PHASE 0 — COMPLETE AUDIT

### 1. CSV Ingestion (`csv_ingestion_service.py`)
- **FEATURE**: Upload and parse CSV to complaints.
- **CURRENT IMPLEMENTATION**: Reads CSV, uses a naive duplicate check (`description`, `latitude`, `longitude`), and creates a new `Complaint` object with a freshly generated UUID. 
- **ACTUAL STATUS**: PARTIALLY WORKING / BUGGY
- **DATA SOURCE**: Uploaded CSV
- **DATABASE TABLE**: `csv_imports`, `complaints`
- **API**: `POST /api/v1/ingest/csv`
- **DEPENDENCIES**: pandas, sqlalchemy
- **PROBLEM**: Does NOT use the CSV's `complaint_id`. If the exact same file is uploaded, the duplicate check might sometimes fail (or if descriptions slightly differ in whitespace), creating duplicates. More importantly, because `complaint_id` is newly generated each time, re-uploading breaks idempotency.
- **RECOMMENDED FIX**: Use the source `complaint_id` from the CSV as the primary key. Upsert instead of insert-if-not-found to guarantee true idempotency.

### 2. Complaint Clustering (`clustering_service.py`)
- **FEATURE**: Groups complaints into failure clusters.
- **CURRENT IMPLEMENTATION**: Uses DBSCAN + TF-IDF semantic similarity + spatial + temporal rules.
- **ACTUAL STATUS**: WORKING
- **DATA SOURCE**: `complaints` table
- **DATABASE TABLE**: `failure_clusters`
- **API**: `POST /api/v1/complaints/cluster`
- **DEPENDENCIES**: scikit-learn
- **PROBLEM**: While the algorithm is reasonable, it lacks proper persistence or updating.
- **RECOMMENDED FIX**: Ensure deterministic clustering based strictly on data, without arbitrary defaults causing unexpected behavior.

### 3. Failure Case Creation (`failure_analysis_service.py`)
- **FEATURE**: Promotes a cluster to a failure case and attaches evidence, history, and hypotheses.
- **CURRENT IMPLEMENTATION**: Generates a `FailureCase` and dynamically generates synthetic `Evidence` and `HistoricalIncident` records using random number generation (`random.randint`, `random.seed`).
- **ACTUAL STATUS**: MOCK / RANDOM
- **DATA SOURCE**: Generated dynamically on creation.
- **DATABASE TABLE**: `failure_cases`, `evidence`, `failure_hypotheses`, `historical_incidents`
- **API**: `POST /api/v1/cases/from-cluster/{cluster_id}`
- **DEPENDENCIES**: sqlalchemy
- **PROBLEM**: Uses `random` module to generate historical dates and creates hard-coded mock evidence (e.g., Rainfall, Terrain, Drainage) for every case. This causes "random cases" and "disconnected objects". 
- **RECOMMENDED FIX**: Remove all `random.*` generation. Create deterministic demo data (synthetic but relational and persistent) during a seed process, or derive evidence strictly from available datasets without randomizing.

### 4. Intervention Engine (`intervention_engine.py`)
- **FEATURE**: Generates intervention options.
- **CURRENT IMPLEMENTATION**: Hard-codes lists of interventions based on failure type, then uses `random.uniform` and `random.seed` to apply variance to costs and durations.
- **ACTUAL STATUS**: MOCK / RANDOM
- **DATA SOURCE**: Internal logic
- **DATABASE TABLE**: `intervention_options`
- **API**: `POST /api/v1/cases/{case_id}/interventions/generate`
- **DEPENDENCIES**: sqlalchemy
- **PROBLEM**: Generates random variance on every run.
- **RECOMMENDED FIX**: Use deterministic logic based on cluster severity, area size, and actual complaint counts. No `random` module.

### 5. Resolution Plan & Work Orders
- **FEATURE**: Decision support, planning, execution tasks.
- **CURRENT IMPLEMENTATION**: Exists in domain models and API routes, but mostly unlinked from real frontend actions or deeply integrated into the lifecycle. 
- **ACTUAL STATUS**: PARTIALLY WORKING / DISCONNECTED
- **DATA SOURCE**: User input (Decisions) / Backend generation (Plans)
- **DATABASE TABLE**: `resolution_plans`, `work_orders`, `work_order_tasks`, `execution_events`
- **API**: `POST /api/v1/cases/{case_id}/plan/{intervention_id}`
- **PROBLEM**: Likely untested in a full E2E flow. Needs to properly persist state.
- **RECOMMENDED FIX**: Enforce strict relational creation. 

### 6. Field Evidence, Verification, Outcome, Infrastructure Memory
- **FEATURE**: Final stages of the lifecycle.
- **CURRENT IMPLEMENTATION**: Domain models exist. APIs are in `execution.py` and `outcomes.py`.
- **ACTUAL STATUS**: MISSING / DISCONNECTED
- **DATABASE TABLE**: `field_evidence`, `verifications`, `outcome_observations`, `infrastructure_memory`
- **PROBLEM**: Barely implemented or completely missing from end-to-end integration. "Infrastructure memory not implemented."
- **RECOMMENDED FIX**: Complete the implementation of these tables and APIs, ensuring deterministic linkage from `Site` -> `InfrastructureMemory`.

---

## PHASE 1 — THE CURRENT CORE FAILURE
The core architectural failure is **Lack of Deterministic Idempotency & Reliance on Random Generation**:
1. **Ingestion Identity**: Since ingestion generates random UUIDs instead of using stable source IDs, data duplicates accumulate on re-uploads or multiple processing runs. 
2. **Synthetic Data via Randomization**: The `FailureAnalysisService` and `InterventionEngine` use Python's `random` module to inject data. This means every time you load or generate, the data shifts, cases change dates, and interventions change costs. 
3. **Disconnection**: Because IDs keep changing and mock data is injected on-the-fly, frontend requests for specific cases or histories either find nothing (404) or find wildly inconsistent data.

**Root Cause Fix required:**
1. Fix `csv_ingestion_service.py` to use `complaint_id` directly for deterministic upserts.
2. Remove ALL `import random` from services. Replace with purely deterministic rules.
3. Build a true "seed" script that establishes a persistent, deterministic "Canonical Demo Dataset".
