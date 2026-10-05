# Civic Pulse Backend Manual Test Guide

This guide is designed for developers verifying the Civic Pulse backend implementation or running demonstrations.

## Automated Verification
The easiest way to verify the entire system is by running the automated End-to-End test suite which covers the complete system lifecycle (Steps 1 through 24).

```bash
cd backend
python e2e_test_full.py
```
This script will ingest standard demonstration data, synthesize cases, predict interventions, and complete a full Work Order pipeline.

## Manual API Exploration (Postman / Swagger)

The backend provides a Swagger UI at: `http://localhost:8000/docs`.

### 1. Ingest Canonical Data
To initialize the system, start with the canonical CSV ingestion endpoint.
- **Endpoint:** `POST /api/v1/ingest/csv`
- **Result:** Loads 20 demonstration complaints into the system.

### 2. Synthesize Case from Baner Cluster
Find the cluster ID associated with the Baner location in Pune.
- **Endpoint:** `GET /api/v1/complaints/clusters/all`
- **Action:** Look for the cluster near `18.559, 73.787` (Baner Road).
- **Endpoint:** `POST /api/v1/cases/from-cluster/{cluster_id}`

### 3. Generate and Approve Resolution Plan
- **Endpoint:** `POST /api/v1/cases/{case_id}/interventions/generate`
- **Endpoint:** `POST /api/v1/cases/{case_id}/analyze`
- Choose the highest ranked intervention and generate a plan:
- **Endpoint:** `POST /api/v1/cases/{case_id}/plan/{intervention_id}`
- Approve the plan:
- **Endpoint:** `POST /api/v1/execution/plans/{plan_id}/approve` (Body: `{"decision": "APPROVED", "approved_by": "admin"}`)

### 4. Work Order Execution and Field Evidence
Once a work order is created (`POST /api/v1/execution/plans/{plan_id}/work-order`), you can simulate task execution.
- **Endpoint:** `POST /api/v1/execution/tasks/{task_id}/start`
- **Endpoint:** `POST /api/v1/execution/tasks/{task_id}/delay` (to test dynamic replanning)
- **Endpoint:** `POST /api/v1/execution/tasks/{task_id}/complete`

**Important Geospatial Requirement:** 
When submitting field evidence to `POST /api/v1/execution/evidence`, the system performs Haversine distance tracking to ensure the engineer is physically present.
To pass the Baner location check, you MUST use coordinates approximately:
- **Latitude:** `18.559`
- **Longitude:** `73.787`
Using arbitrary coordinates (like `19.112, -72.1`) will result in a `MISMATCH` verification status and `LOW` confidence rating.

### 5. Review Infrastructure Memory
Once the work order is verified and outcomes are recorded, view the aggregated infrastructure memory for the specific site.
- **Endpoint:** `GET /api/v1/outcomes/sites/{site_id}/memory`
This aggregates historical patterns, recurrence rates, and intervention effectiveness.
