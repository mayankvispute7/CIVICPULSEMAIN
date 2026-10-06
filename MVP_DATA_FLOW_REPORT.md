# MVP Data Flow Report
**CIVIC PULSE 10-Step Workflow Data Model**

This report documents the exact data entities and relationships implemented in the SQLite database to power the complete end-to-end demonstration.

## The Core Thread: `case_id`
All data in the 10-step lifecycle revolves around the `FailureCase` entity (Primary Key: `case_id`). From initial clustering to final outcome logging, foreign keys rigidly attach every observation, plan, and event to this case.

## Stage-by-Stage Data Links

1. **Understand (Case Overview)**
   - **Entity:** `FailureCase`
   - **Data Served:** Basic info, `recurrence_count`, `impact_summary`, `fingerprint` JSON, and `failure_chain` graph structure.
   - **Source:** Seeded directly via `seed_db.py` logic representing model estimations based on 18 complaints in Kothrud-Bavdhan.

2. **Investigate (Evidence)**
   - **Entity:** `Evidence`
   - **Link:** `case_id`
   - **Data Served:** 6 distinct evidence types (e.g. Complaint concentration, Rainfall correlation, Topography, Infrastructure) supporting the primary waterlogging case.

3. **History (Historical Context)**
   - **Entity:** `HistoricalIncident`
   - **Link:** `case_id` (and `site_id`)
   - **Data Served:** Past incidents recorded at this specific site, proving the "Recurring" nature of the waterlogging.

4. **Predict (Future Risk)**
   - **Entity:** `Prediction`
   - **Link:** `case_id`
   - **Data Served:** The "Do Nothing" baseline projection detailing 5-year exposure risk and assumptions if no intervention is selected.

5. & 6. **Simulate & Decide (Intervention Engine)**
   - **Entities:** `InterventionOption`, `InterventionConstraint`, `DecisionAnalysis`
   - **Link:** `case_id`
   - **Data Served:** The backend `InterventionEngine` generates 8 waterlogging-specific options. After constraints are applied, these are scored and ranked.

7. **Execute (Work Order & Tasks)**
   - **Entities:** `ResolutionPlan`, `WorkOrder`, `WorkOrderTask`, `ReplanEvent`
   - **Link:** `case_id` -> `plan_id` -> `work_order_id`
   - **Data Served:** The selected "Drain Repair" intervention is converted to an approved work order with sequential tasks. A simulated dynamic `ReplanEvent` (Worker illness) demonstrates agility.

8. **Verify (Field Inspections)**
   - **Entities:** `FieldEvidence`, `Verification`
   - **Link:** `work_order_id`
   - **Data Served:** Simulated GPS-tagged photos from field crews and automated verification checks resulting in a PASSED status.

9. **Outcome (Before/After)**
   - **Entity:** `OutcomeObservation`
   - **Link:** `case_id`, `work_order_id`
   - **Data Served:** The next comparable rain event triggers an outcome comparison showing complaints dropping from 18 to 6.

10. **Memory (Infrastructure Learning)**
    - **Entity:** `InfrastructureMemory`
    - **Link:** `site_id`
    - **Data Served:** High-level aggregation showing total interventions over time and explicit natural-language learning patterns for future recommendations.

## Data Truth System
Each record is explicitly tagged with a `DataTruth` enum flag (e.g., `SYNTHETIC_DATA`, `IMPORTED_DATA`, `MODEL_ESTIMATION`) to strictly demarcate real city data from AI-generated demonstration pathways.
