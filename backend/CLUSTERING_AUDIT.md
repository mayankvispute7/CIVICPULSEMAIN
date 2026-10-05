# Civic Pulse Clustering Engine Audit

## 1. Algorithm Overview
The current clustering engine uses a two-step approach:
1. **Spatial Grouping:** Uses DBSCAN to group complaints based purely on geographic proximity.
2. **Temporal Splitting:** Iterates through spatial clusters and splits them if the time gap between complaints exceeds a temporal threshold.

## 2. Input Features and Their Role
| Feature | Role in Clustering | Role in Confidence Scoring |
| :--- | :--- | :--- |
| **Spatial Proximity** | **Primary driver**. Groups complaints within `eps` radius. | Yes (30% weight based on cluster tightness) |
| **Temporal Proximity** | **Secondary driver**. Splits clusters that span too much time. | No |
| **Semantic Similarity** | **Ignored** during clustering. | Yes (25% weight) |
| **Complaint Category** | **Ignored** during clustering. | Yes (20% weight based on category homogeneity) |
| **Rainfall / Events** | **Ignored**. | No |
| **Infrastructure Context** | **Ignored**. | No |

## 3. Thresholds
*   `CLUSTERING_SPATIAL_EPS_METERS`: Default 500m. Maximum distance between points to be considered neighbors in DBSCAN.
*   `CLUSTERING_MIN_SAMPLES`: Default 3. Minimum complaints to form a cluster.
*   `CLUSTERING_TEMPORAL_DAYS`: Default 90 days. Used to split spatial clusters that span a larger timeframe.

## 4. Confidence Calculation
The confidence score is a weighted sum (clamped between 0.1 and 0.99):
*   **30% Spatial Score:** `max(0, 1.0 - (spatial_radius / 2000.0))`
*   **25% Count Score:** `min(1.0, len(complaints) / 20.0)`
*   **25% Semantic Score:** Average pairwise cosine similarity of TF-IDF vectors of complaint descriptions.
*   **20% Category Coherence:** `max(0, 1.0 - (category_count - 1) * 0.2)`

## 5. Known Weaknesses
1.  **Overwhelming Spatial Bias:** If an unrelated pothole, streetlight failure, and waterlogging complaint happen within 500m of each other within 90 days, they **will be merged** into a single cluster. Spatial proximity is incorrectly treated as sufficient evidence of a shared underlying failure.
2.  **Semantic Similarity Disconnect:** The TF-IDF cosine similarity score averages 0.06 because the raw text descriptions differ drastically (e.g., "water entered shop" vs. "traffic is slow"). A low score drops the confidence but does not split the cluster, leading to low-confidence "junk" clusters rather than distinct, high-confidence clusters.
3.  **Incident Count Bug:** The code calculated distinct incident episodes based on a 48-hour window but failed to pass this value to the cluster model, instead hardcoding `incident_count = len(member_complaints)`.
4.  **No Mechanism Recognition:** The engine does not recognize that certain complaint types (e.g., Blocked Inlet -> Waterlogging -> Traffic Disruption) form a logical failure chain.
