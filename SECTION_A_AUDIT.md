# SECTION A AUDIT

## Overview
This audit maps the current state of Section A (DATA INGESTION → RECURRENCE PREDICTION) and classifies the disposition of each component (KEEP, REPAIR, REBUILD, REMOVE, NOT IMPLEMENTED).

## Tracing the Flow & Component Classification

### 1. CSV / PDF INGESTION
- **Location:** `app/services/csv_ingestion_service.py`
- **State:** Reads CSV, maps columns, deduplicates, and creates `Complaint` objects. 
- **Issues:** PDF Ingestion is missing. 
- **Classification:** **REPAIR** (Enhance CSV handling if needed) / **NOT IMPLEMENTED** (PDF).

### 2. COMPLAINT CLUSTERING
- **Location:** `app/services/clustering_service.py`
- **State:** Recently rebuilt. It correctly uses a multi-signal affinity matrix (Spatial, Temporal, Semantic TF-IDF, Infrastructure) to group complaints into `FailureCluster` records. Incident episodes are dynamically calculated.
- **Classification:** **KEEP**.

### 3. GEOSPATIAL INTELLIGENCE
- **Location:** `app/services/geospatial_service.py`
- **State:** Simple Haversine distance and centroid calculation. Creates `Site` records.
- **Classification:** **KEEP**.

### 4. FAILURE CASE GENERATION
- **Location:** `app/services/failure_analysis_service.py` (`create_case_from_cluster`)
- **State:** Promotes a cluster to a case, but heavily relies on synthetic data to fill the case details.
- **Classification:** **REBUILD**.

### 5. CURRENT EVIDENCE
- **Location:** `app/services/failure_analysis_service.py` (`_generate_evidence`)
- **State:** Hardcoded fake data (Rainfall, Terrain, Drainage capacity) marked as "synthetic for demo".
- **Classification:** **REMOVE / REBUILD** (Must implement real data pipelines or factual heuristics derived from the cluster).

### 6. HISTORICAL DATA
- **Location:** `app/services/failure_analysis_service.py` (`_generate_historical_incidents`)
- **State:** Uses `random.randint` to spawn fake past incidents (Fake AI).
- **Classification:** **REMOVE / REBUILD** (Must query actual historical closed cases/complaints in the database).

### 7. ROOT-CAUSE HYPOTHESIS
- **Location:** `app/services/failure_analysis_service.py` (`_generate_hypotheses`)
- **State:** Hardcoded generic strings ("Drainage capacity/connectivity constraint") applied blindly based on cluster categories.
- **Classification:** **REBUILD** (Should derive hypotheses from the `relationship_evidence` calculated during clustering).

### 8. RECURRENCE PREDICTION
- **Location:** `app/services/intervention_engine.py` (`create_predictions`)
- **State:** Hardcoded `expected_months_to_recurrence` based on generic template assumptions. Technically owned by Section A but tightly coupled to InterventionEngine (Section B).
- **Classification:** **REPAIR / EXTRACT** (Decouple baseline prediction logic from Interventions so Section A can independently predict baseline recurrence).

## High-Risk Findings

1. **Fake AI Claims / Hackathon Shortcuts:** The entire Failure Analysis layer (`failure_analysis_service.py`) is essentially a mock data generator designed for a hackathon demo. It generates fake evidence, fake history, and fake hypotheses using `random`. This completely compromises the integrity of Section A.
2. **Boundary Bleed:** Recurrence prediction belongs to Section A, but is currently implemented inside `intervention_engine.py` which belongs to Section B.
3. **Data Truth Flags:** The models have `data_truth` fields, and currently many records are correctly flagged as `SYNTHETIC_DATA`, but the frontend blindly renders them as actionable intelligence.
