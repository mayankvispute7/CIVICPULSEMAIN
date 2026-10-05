# SECTION A IMPLEMENTATION PLAN

## Overview
This document defines the exact dependency order for rebuilding Section A. The core objective is to replace hackathon-era fake data generation with deterministic, fact-based logic.

**CRITICAL RULE:** Do not modify Section B (`intervention_engine.py`, Work Orders, Execution) unless strictly required for a shared boundary contract (e.g., extracting predictions).

## Dependency Order and Execution Steps

### Phase 1: Clean Foundation (Remove Fake AI)
1. **Target:** `app/services/failure_analysis_service.py`
2. **Action:** Strip out `random` historical incident generation, hardcoded synthetic DEM/drainage evidence, and fake rainfall correlations. 
3. **Reason:** We cannot build real intelligence on a hackathon data-faker. Cases must reflect actual ingested facts.

### Phase 2: Authentic Evidence & Historical Matcher
1. **Target:** `failure_analysis_service.py`
2. **Action:** Implement a real Historical Data matcher. When a new case is generated, it should query the database for *actual* past closed cases/complaints at the same `Site` instead of using `random`.
3. **Action:** Implement dynamic Evidence aggregation. Evidence should only reflect facts (e.g., "Cluster contains X severe complaints", "Cluster spans Y days", "Z distinct incidents identified") instead of hallucinating DEM terrain data.

### Phase 3: Root-Cause Hypothesis Generation
1. **Target:** `failure_analysis_service.py`
2. **Action:** Rewrite `_generate_hypotheses` to use the actual `relationship_evidence` calculated by the `ClusteringService`. 
    - *Example:* If the cluster formed primarily due to temporal spikes across a wide area, hypothesize a systemic weather trigger. 
    - *Example:* If spatial density is extremely high but temporal spread is wide, hypothesize localized infrastructure collapse/blockage.

### Phase 4: Prediction Extraction (Boundary Sync)
1. **Target:** `app/services/intervention_engine.py` (Section B) → `app/services/failure_analysis_service.py` (Section A)
2. **Action:** Extract the baseline "Do Nothing" recurrence prediction logic from Section B's intervention engine and migrate it to Section A. Section A owns *Recurrence Prediction* and must predict the baseline recurrence (when, where, how often) *before* Section B decides what interventions to apply.

### Phase 5: PDF Data Ingestion
1. **Target:** `app/services/csv_ingestion_service.py` -> `data_ingestion_service.py`
2. **Action:** Implement PDF parsing for unstructured or tabular reports to map to the `Complaint` model.

### Phase 6: API and Frontend Verification
1. **Target:** `app/schemas/api_schemas.py`, `frontend/src/app/cases`
2. **Action:** Ensure the frontend consumes the newly structured, real evidence, history, and hypothesis schemas without breaking.

---
**Status:** READY TO COMMENCE PHASE 1.
