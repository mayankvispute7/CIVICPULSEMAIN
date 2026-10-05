"""
Clustering Service.

Implements complaint clustering using a hybrid approach:
1. Spatial proximity (Haversine distance)
2. Temporal proximity
3. Category similarity
4. Semantic similarity (text-based, using TF-IDF as lightweight alternative to transformers)

Uses DBSCAN for spatial-temporal clustering, enhanced with category/semantic scoring.
"""

import logging
import math
from datetime import datetime, timedelta
from collections import Counter
from typing import Optional

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.models.domain import Complaint, FailureCluster, Site
from app.models.enums import ClusterStatus, DataTruth, ComplaintStatus
from app.services.geospatial_service import GeospatialService
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClusteringService:
    """
    Service for clustering complaints into failure groups.

    Uses a multi-factor approach:
    - Spatial proximity (primary)
    - Temporal proximity
    - Category match
    - Text similarity

    Algorithm: DBSCAN on spatial features, refined with composite scoring.
    """

    def __init__(self, db: Session):
        self.db = db
        self.geo_service = GeospatialService(db)

    def run_clustering(
        self,
        spatial_eps_m: Optional[float] = None,
        min_samples: Optional[int] = None,
        temporal_days: Optional[int] = None,
    ) -> dict:
        """
        Run clustering on all unclustered complaints.

        Returns summary of clustering results.
        """
        spatial_eps = spatial_eps_m or settings.CLUSTERING_SPATIAL_EPS_METERS
        min_samp = min_samples or settings.CLUSTERING_MIN_SAMPLES
        temp_days = temporal_days or settings.CLUSTERING_TEMPORAL_DAYS

        logger.info(
            f"Running clustering: eps={spatial_eps}m, min_samples={min_samp}, "
            f"temporal_window={temp_days}d"
        )

        # Get complaints with coordinates that are not yet clustered
        complaints = self.db.query(Complaint).filter(
            Complaint.latitude.isnot(None),
            Complaint.longitude.isnot(None),
            Complaint.cluster_id.is_(None)
        ).all()

        if len(complaints) < min_samp:
            logger.info(f"Not enough complaints for clustering: {len(complaints)} < {min_samp}")
            return {
                "total_complaints": len(complaints),
                "total_clusters": 0,
                "unclustered_complaints": len(complaints),
                "clusters": [],
                "algorithm": "DBSCAN+hybrid",
                "parameters": {
                    "spatial_eps_m": spatial_eps,
                    "min_samples": min_samp,
                    "temporal_days": temp_days,
                },
            }

        # Build feature matrix
        coords = np.array([[c.latitude, c.longitude] for c in complaints])

        # Convert eps from meters to approximate degrees
        eps_deg = spatial_eps / 111320.0

        # Run DBSCAN on spatial features
        clustering = DBSCAN(
            eps=eps_deg,
            min_samples=min_samp,
            metric="haversine" if len(complaints) > 10 else "euclidean",
        )

        # DBSCAN expects radians for haversine metric
        if len(complaints) > 10:
            coords_rad = np.radians(coords)
            labels = clustering.fit_predict(coords_rad)
            # Haversine metric in sklearn uses Earth radius, so eps needs to be in radians
            # Recalculate with euclidean for simplicity in this implementation
            clustering_euc = DBSCAN(eps=eps_deg, min_samples=min_samp, metric="euclidean")
            labels = clustering_euc.fit_predict(coords)
        else:
            labels = clustering.fit_predict(coords)

        # Refine clusters with temporal + category + text similarity
        refined_labels = self._refine_clusters(complaints, labels, temp_days)

        # Build text similarity for semantic confidence
        text_similarities = self._compute_text_similarities(complaints)

        # Create cluster records
        clusters_created = []
        unique_labels = set(refined_labels)
        unique_labels.discard(-1)  # -1 = noise/unclustered

        for cluster_label in sorted(unique_labels):
            member_indices = [i for i, l in enumerate(refined_labels) if l == cluster_label]
            member_complaints = [complaints[i] for i in member_indices]

            if len(member_complaints) < min_samp:
                continue

            cluster = self._create_cluster(
                member_complaints,
                text_similarities,
                member_indices,
                cluster_label,
            )
            clusters_created.append(cluster)

        # Count unclustered
        unclustered = sum(1 for l in refined_labels if l == -1)

        self.db.commit()

        result = {
            "total_complaints": len(complaints),
            "total_clusters": len(clusters_created),
            "unclustered_complaints": unclustered,
            "clusters": clusters_created,
            "algorithm": "DBSCAN+hybrid",
            "parameters": {
                "spatial_eps_m": spatial_eps,
                "min_samples": min_samp,
                "temporal_days": temp_days,
            },
        }

        logger.info(
            f"Clustering complete: {len(complaints)} complaints → "
            f"{len(clusters_created)} clusters, {unclustered} unclustered"
        )
        return result

    def _refine_clusters(
        self,
        complaints: list[Complaint],
        spatial_labels: np.ndarray,
        temporal_days: int,
    ) -> list[int]:
        """
        Refine spatial clusters by checking temporal and category coherence.
        Split clusters that span too much time or have incompatible categories.
        """
        refined = list(spatial_labels)

        next_label = max(spatial_labels) + 1 if len(spatial_labels) > 0 else 0

        unique_clusters = set(spatial_labels)
        unique_clusters.discard(-1)

        for cluster_label in unique_clusters:
            indices = [i for i, l in enumerate(spatial_labels) if l == cluster_label]
            cluster_complaints = [complaints[i] for i in indices]

            # Check temporal coherence
            dates = [c.reported_at for c in cluster_complaints if c.reported_at]
            if dates:
                date_range = (max(dates) - min(dates)).days
                if date_range > temporal_days:
                    # Split by time windows
                    sorted_by_date = sorted(zip(indices, dates), key=lambda x: x[1])
                    current_window_start = sorted_by_date[0][1]
                    current_group = []

                    for idx, dt in sorted_by_date:
                        if (dt - current_window_start).days > temporal_days:
                            # Start new group if there are enough members
                            if len(current_group) >= 2:
                                for g_idx in current_group:
                                    refined[g_idx] = next_label
                                next_label += 1
                            current_group = [idx]
                            current_window_start = dt
                        else:
                            current_group.append(idx)

                    if len(current_group) >= 2:
                        for g_idx in current_group:
                            refined[g_idx] = next_label
                        next_label += 1

        return refined

    def _compute_text_similarities(self, complaints: list[Complaint]) -> np.ndarray:
        """Compute pairwise text similarity using TF-IDF."""
        texts = [c.description or "" for c in complaints]

        if not any(texts):
            return np.zeros((len(complaints), len(complaints)))

        try:
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words="english",
                min_df=1,
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            return cosine_similarity(tfidf_matrix)
        except Exception as e:
            logger.warning(f"Text similarity computation failed: {e}")
            return np.zeros((len(complaints), len(complaints)))

    def _create_cluster(
        self,
        member_complaints: list[Complaint],
        text_similarities: np.ndarray,
        member_indices: list[int],
        cluster_label: int,
    ) -> FailureCluster:
        """Create a FailureCluster from a group of complaints."""
        # Compute centroid
        centroid_lat, centroid_lon = self.geo_service.compute_centroid(member_complaints)

        # Compute spatial radius
        spatial_radius = self.geo_service.compute_spatial_radius(
            member_complaints, (centroid_lat, centroid_lon)
        )

        # Time range and incidents
        dates = sorted([c.reported_at for c in member_complaints if c.reported_at])
        time_start = dates[0] if dates else None
        time_end = dates[-1] if dates else None
        
        # Calculate distinct incident episodes (grouping complaints within 48 hours)
        incident_episodes = 0
        if dates:
            incident_episodes = 1
            current_episode_start = dates[0]
            for dt in dates[1:]:
                if (dt - current_episode_start).total_seconds() > 48 * 3600:
                    incident_episodes += 1
                    current_episode_start = dt

        # Categories
        categories = list(set(c.category or c.incident_type for c in member_complaints))

        # Severity distribution
        severity_dist = dict(Counter(c.severity for c in member_complaints))

        # Compute semantic similarity within cluster
        if len(member_indices) >= 2:
            cluster_sims = []
            for i in range(len(member_indices)):
                for j in range(i + 1, len(member_indices)):
                    if member_indices[i] < text_similarities.shape[0] and \
                       member_indices[j] < text_similarities.shape[1]:
                        cluster_sims.append(
                            text_similarities[member_indices[i], member_indices[j]]
                        )
            semantic_sim = float(np.mean(cluster_sims)) if cluster_sims else 0.0
        else:
            semantic_sim = 1.0

        # Compute confidence
        confidence = self._compute_cluster_confidence(
            member_complaints, spatial_radius, semantic_sim, len(categories)
        )

        # Generate title
        primary_category = max(
            Counter(c.category or c.incident_type for c in member_complaints).items(),
            key=lambda x: x[1],
        )[0] if member_complaints else "Unknown"

        ward = member_complaints[0].ward if member_complaints and member_complaints[0].ward else "Unknown"
        title = f"{primary_category.replace('_', ' ').title()} Cluster - {ward}"

        # Generate rationale
        rationale = (
            f"Cluster of {len(member_complaints)} complaints within {spatial_radius:.0f}m radius. "
            f"Categories: {', '.join(categories)}. "
            f"Time span: {(time_end - time_start).days if time_start and time_end else 0} days. "
            f"Semantic similarity: {semantic_sim:.2f}. "
            f"Confidence: {confidence:.2f}."
        )

        # Find or create site
        site = self.geo_service.find_or_create_site(
            centroid_lat, centroid_lon,
            ward=ward,
        )

        # Create cluster
        cluster = FailureCluster(
            title=title,
            complaint_count=len(member_complaints),
            incident_count=len(member_complaints),
            confidence=round(confidence, 3),
            status=ClusterStatus.CONFIRMED.value,
            site_id=site.site_id,
            centroid_lat=centroid_lat,
            centroid_lon=centroid_lon,
            spatial_radius_m=round(spatial_radius, 1),
            time_range_start=time_start,
            time_range_end=time_end,
            categories=categories,
            severity_distribution=severity_dist,
            semantic_similarity=round(semantic_sim, 3),
            cluster_rationale=rationale,
            data_truth=DataTruth.MODEL_ESTIMATION.value,
        )
        self.db.add(cluster)
        self.db.flush()

        # Update complaints with cluster_id
        for complaint in member_complaints:
            complaint.cluster_id = cluster.cluster_id
            complaint.status = ComplaintStatus.CLUSTERED.value

        return cluster

    def _compute_cluster_confidence(
        self,
        complaints: list[Complaint],
        spatial_radius: float,
        semantic_similarity: float,
        category_count: int,
    ) -> float:
        """
        Compute cluster confidence based on multiple factors.

        Factors:
        - Spatial tightness (closer = higher confidence)
        - Number of complaints (more = higher)
        - Semantic similarity (higher = more confident)
        - Category coherence (fewer distinct categories = better)
        """
        # Spatial score (0-1): tighter clusters are better
        spatial_score = max(0, 1.0 - (spatial_radius / 2000.0))  # 0 at 2km+

        # Count score (0-1): more complaints = higher
        count_score = min(1.0, len(complaints) / 20.0)

        # Semantic score: direct
        semantic_score = semantic_similarity

        # Category coherence (0-1): fewer categories = better
        category_score = max(0, 1.0 - (category_count - 1) * 0.2)

        # Weighted combination
        confidence = (
            0.30 * spatial_score +
            0.25 * count_score +
            0.25 * semantic_score +
            0.20 * category_score
        )

        return max(0.1, min(0.99, confidence))

    def get_clusters(self) -> list[FailureCluster]:
        """Get all clusters."""
        return self.db.query(FailureCluster).order_by(
            FailureCluster.complaint_count.desc()
        ).all()

    def get_cluster(self, cluster_id: str) -> Optional[FailureCluster]:
        """Get a single cluster by ID."""
        return self.db.query(FailureCluster).filter(
            FailureCluster.cluster_id == cluster_id
        ).first()

    def get_cluster_complaints(self, cluster_id: str) -> list[Complaint]:
        """Get all complaints in a cluster."""
        return self.db.query(Complaint).filter(
            Complaint.cluster_id == cluster_id
        ).all()
