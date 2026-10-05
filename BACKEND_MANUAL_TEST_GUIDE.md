# Civic Pulse - Backend Manual Test Guide

This guide provides step-by-step instructions for manually testing the entire backend lifecycle using `curl` or any API client (like Postman).

Ensure the server is running on `http://localhost:8000`.

To start the server:
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

## 1. System Health
Check if the server and database are alive.
```bash
curl -X GET "http://localhost:8000/health"
```
*Expected: 200 OK with `{"status": "ok", ...}`*

## 2. Ingest CSV Data
We will upload a test CSV file to the system. 
Create a file named `test_complaints.csv`:
```csv
complaint_id,date,description,address,ward,latitude,longitude,category,severity
C001,2026-07-01 10:00:00,Severe waterlogging after heavy rain,Main St,Ward A,19.112,-72.100,WATERLOGGING,HIGH
C002,2026-07-02 11:30:00,Road completely flooded,Park Ave,Ward A,19.113,-72.101,FLOODING,CRITICAL
C003,2026-07-03 09:15:00,Drain overflowing onto street,Elm St,Ward A,19.111,-72.102,DRAINAGE,HIGH
C004,2026-07-15 14:00:00,Pothole causing accidents,Oak St,Ward B,19.250,-72.250,POTHOLE,MEDIUM
```

Upload via API:
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/csv" \
  -F "file=@test_complaints.csv" \
  -F "data_truth=REAL_DATA"
```
*Expected: Returns an `ImportSummary` with `accepted_rows: 4`.*

## 3. Run Clustering
Now, group those spatial complaints into failure clusters.
```bash
curl -X POST "http://localhost:8000/api/v1/complaints/cluster?spatial_eps_m=500&min_samples=2&temporal_days=14"
```
*Expected: Returns clustering summary. Should find 1 cluster for Ward A (the 3 waterlogging/drainage complaints) and leave the Ward B pothole unclustered.*

Get the Cluster ID from the response or list clusters:
```bash
curl -X GET "http://localhost:8000/api/v1/complaints/clusters/all"
```
*Note the `cluster_id`.*

## 4. Generate Failure Case
Translate the cluster into an actionable investigated case.
```bash
# Replace <CLUSTER_ID> with the actual ID
curl -X POST "http://localhost:8000/api/v1/cases/from-cluster/<CLUSTER_ID>"
```
*Expected: Returns a `FailureCase` with a generated failure chain, hypotheses, and synthetic evidence.*

## 5. Intervention Planning
Generate possible interventions to fix the failure case.
```bash
# Replace <CASE_ID> with the actual ID from step 4
curl -X POST "http://localhost:8000/api/v1/cases/<CASE_ID>/interventions/generate"
```
*Expected: Returns a list of interventions (e.g., Drain Cleaning, Capacity Upgrade).*

Apply constraints (e.g., budget limit):
```bash
curl -X POST "http://localhost:8000/api/v1/cases/<CASE_ID>/constraints" \
  -H "Content-Type: application/json" \
  -d '{"budget_limit": 100000, "deadline": "2026-08-01T00:00:00Z"}'
```

Run decision analysis to rank interventions:
```bash
curl -X POST "http://localhost:8000/api/v1/cases/<CASE_ID>/analyze"
```
*Expected: Returns a ranked list of interventions with `score_breakdown`.*

## 6. Create Resolution Plan & Work Order
Select the top intervention to create a plan.
```bash
# Replace <INTERVENTION_ID> with the top ranked ID
curl -X POST "http://localhost:8000/api/v1/cases/<CASE_ID>/plan/<INTERVENTION_ID>"
```

Approve the plan:
```bash
# Replace <PLAN_ID> with the generated plan ID
curl -X POST "http://localhost:8000/api/v1/execution/plans/<PLAN_ID>/approve" \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "Chief Engineer", "decision": "APPROVED"}'
```

Create the Work Order:
```bash
curl -X POST "http://localhost:8000/api/v1/execution/plans/<PLAN_ID>/work-order"
```
*Note the `work_order_id`.*

## 7. Execution and Verification
List tasks for the work order:
```bash
curl -X GET "http://localhost:8000/api/v1/execution/work-orders/<WORK_ORDER_ID>/tasks"
```

Start the first task:
```bash
# Replace <TASK_ID> with the first task ID
curl -X POST "http://localhost:8000/api/v1/execution/tasks/<TASK_ID>/start"
```

Complete the first task:
```bash
curl -X POST "http://localhost:8000/api/v1/execution/tasks/<TASK_ID>/complete" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Completed successfully"}'
```

Submit Field Evidence for verification:
```bash
curl -X POST "http://localhost:8000/api/v1/execution/evidence" \
  -H "Content-Type: application/json" \
  -d '{
    "work_order_id": "<WORK_ORDER_ID>",
    "latitude": 19.112,
    "longitude": -72.100,
    "captured_at": "2026-07-20T10:00:00Z"
  }'
```

Verify Work Order:
```bash
curl -X POST "http://localhost:8000/api/v1/execution/work-orders/<WORK_ORDER_ID>/verify" \
  -H "Content-Type: application/json" \
  -d '{"verified_by": "System"}'
```

## 8. Outcomes and Learning
Record an outcome (e.g., during the next rainstorm):
```bash
curl -X POST "http://localhost:8000/api/v1/outcomes" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "<CASE_ID>",
    "observed_at": "2026-08-15T12:00:00Z",
    "status": "IMPROVED",
    "trigger_event": "Heavy Rainfall",
    "complaints_during_event": 0
  }'
```

View generated Prediction vs Reality comparisons:
```bash
curl -X GET "http://localhost:8000/api/v1/outcomes/cases/<CASE_ID>/comparisons"
```

Check Infrastructure Memory for the site:
```bash
# Retrieve Site ID from the Case details
curl -X GET "http://localhost:8000/api/v1/outcomes/sites/<SITE_ID>/memory"
```

*Expected: Returns a long-term aggregated summary of the site, noting the successful intervention and updated confidence.*
