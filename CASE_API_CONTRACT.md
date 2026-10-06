# Case API Contract

This documents the backend API endpoints exposed by FastAPI that power the 10-step case lifecycle.

## Base URL: `/api`

### 1. Ingestion & Situation
- `POST /ingestion/csv`: Upload a complaint CSV.
- `GET /complaints`: List all imported complaints (city level).
- `GET /analysis/clusters`: Retrieve failure clusters (groups of complaints).

### 2. Case Management (Understand & Investigate)
- `GET /cases`: List all active failure cases.
- `GET /cases/{case_id}`: Get the comprehensive case object (includes fingerprint and failure chain).
- `GET /cases/{case_id}/evidence`: Get the evidence ledger for the case.

### 3. History & Prediction
- `GET /cases/{case_id}/history`: Retrieve historical incidents linked to the case's site.
- `GET /cases/{case_id}/predictions`: Get the 5-year screening-level risk predictions (e.g., Do Nothing baseline).

### 4. Intervention Lab (Simulate & Decide)
- `GET /cases/{case_id}/interventions`: Retrieve all generated intervention options.
- `POST /cases/{case_id}/constraints`: Update municipal constraints (budget, deadline, workers).
- `POST /cases/{case_id}/analyze`: Run feasibility and ranking against constraints, returning the recommended option.
- `GET /cases/{case_id}/plan`: Retrieve the final approved resolution plan for the selected intervention.

### 5. Execution (Execute & Verify)
- `GET /execution/work-orders`: List work orders.
- `GET /execution/work-orders/{work_order_id}`: Retrieve a specific work order.
- `GET /execution/work-orders/{work_order_id}/tasks`: Retrieve the sequential execution tasks.
- `GET /execution/work-orders/{work_order_id}/replans`: Retrieve dynamic replanning events (e.g., disruptions).
- `GET /execution/work-orders/{work_order_id}/evidence`: Retrieve field evidence (GPS/Photos) for the work order.
- `GET /execution/work-orders/{work_order_id}/verification`: Retrieve the automated verification checks.

### 6. Outcomes & Memory
- `GET /outcomes/cases/{case_id}`: Retrieve outcome observations (Before/After metrics).
- `GET /outcomes/cases/{case_id}/comparisons`: Retrieve predicted vs observed outcome comparisons.
- `GET /outcomes/cases/{case_id}/learnings`: Extract learned patterns.
- `GET /outcomes/sites/{site_id}/memory`: Retrieve the long-term infrastructure memory for the site.
