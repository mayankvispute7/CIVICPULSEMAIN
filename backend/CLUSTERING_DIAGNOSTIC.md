# Civic Pulse: Clustering Diagnostic Report

## 1. Actual Clustering Implementation Analysis

I have inspected the `backend/app/services/clustering_service.py` and `backend/app/core/config.py`. Here is the exact breakdown of how signals influence clustering:

| Feature | Used for Clustering? | Used for Confidence? | Threshold / Weight |
| :--- | :--- | :--- | :--- |
| **Spatial distance** | **YES** | YES | Threshold: `500m` radius (via DBSCAN `eps`). Weight: 30% of confidence. |
| **Temporal distance** | **YES** | NO | Threshold: `90 days` (`CLUSTERING_TEMPORAL_DAYS`). |
| **Semantic similarity** | NO | YES | Used ONLY for confidence calculation. Weight: 25%. |
| **Complaint category** | NO | YES | Used ONLY for confidence calculation. Weight: 20%. |
| **Rainfall context** | NO | NO | Not currently parsed by the clustering algorithm. |
| **Infrastructure / Context** | NO | NO | Not currently used. |
| **Severity** | NO | NO | Only aggregated for reporting. |

**Conclusion:** The current algorithm is essentially a strict spatio-temporal grouper. `distance < 500m AND time_span < 90 days = SAME CLUSTER`.

## 2. The 0.06 Semantic Similarity
This value represents the **average pairwise cosine similarity** of TF-IDF vectors calculated across the 20 complaint descriptions. 
*   Because the complaints are highly diverse in phrasing (some mention "waterlogging", some "vehicles moving slowly", some "blocked inlet"), they share very few exact keywords. 
*   A score of `0.06` (6%) means the raw text strings are dissimilar. 
*   **Verdict:** This is functioning mathematically correctly, but TF-IDF is a poor tool for understanding that "drain overflow" and "traffic disruption" are semantically linked symptoms.

## 3. Why all 20 complaints were merged
The 20 complaints in `pune_baner_complaints_20.csv` all occurred in the same physical area (Baner Road junction / market) with a spatial spread of only `~100m`. They occurred between `June 14` and `August 12` (a span of 59 days). 

Because the configuration (`config.py`) specifies `CLUSTERING_SPATIAL_EPS_METERS = 500.0` and `CLUSTERING_TEMPORAL_DAYS = 90`, **all 20 complaints easily passed the spatial-temporal threshold and were clumped together by DBSCAN.**

## 4. Test Spatial-Only Failure
If semantic and temporal checks were removed, the result would be exactly the same. The algorithm currently heavily suffers from a spatial-only bias. If an unrelated streetlight failure and a pothole occurred within 500m of each other within 90 days, the current code **would erroneously merge them into one cluster.**

## 5. Incident vs Recurring Failure
You were completely correct: 20 complaints does NOT mean 20 independent incidents. I found a bug in `_create_cluster` where `incident_count = len(member_complaints)` was hardcoded. 
*   **FIXED:** I have updated the logic in `clustering_service.py`. It now groups complaints that happen within 48 hours of each other into distinct "incident episodes." The cluster will now correctly report **3 incident episodes** (Mid-June, Early July, Mid-August).

## 6. High Priority Bug
The UI was incorrectly calculating the "High Priority" metric. Instead of looking at the actual severity of the complaints (15 High, 5 Medium), the frontend `SituationHeader.tsx` was looking for clusters with an overall `confidence > 0.8`. Since the cluster confidence was `0.556`, it reported `0` high priority clusters.
*   **FIXED:** I updated `SituationHeader.tsx` to properly read the `severity_distribution` of the cluster and display the actual number of high-severity complaints.

## 7. The "Failed to load case" Error
In the screenshot, you are getting a "Case not found" error. This is because clicking the cluster takes you to the investigation workspace for a `FailureCase`, but the system hasn't run the `FailureAnalysisService` yet to convert this raw cluster into an active case.

---

### FINAL VERDICT: CLUSTERING LOGIC NEEDS FIX

The 20 complaints *do* belong together, as they are all symptoms of the same recurring Baner Road drainage failure. However, the algorithm arrived at this correct result **by accident** (solely due to geographic proximity). It violates the requirement of ensuring that physically close but completely unrelated complaints are kept separate. The `_refine_clusters` method must be updated to split clusters that have incompatible categories.
