import logging
import math
from datetime import datetime
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

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class ClusteringService:
    def __init__(self, db: Session):
        self.db = db
        self.geo_service = GeospatialService(db)
        
        self.chain_water = {"WATERLOGGING", "FLOODING", "DRAINAGE", "DRAINAGE_OVERFLOW", "BLOCKED_INLET", "SURFACE_RUNOFF", "TRAFFIC_DISRUPTION", "PEDESTRIAN_DISRUPTION", "PRE_RAIN_RISK"}
        self.chain_road = {"ROAD_SURFACE_DAMAGE", "POTHOLE", "ROAD_CAVE_IN"}
        self.chain_light = {"STREETLIGHT_FAILURE", "POLE_DAMAGE", "POWER_OUTAGE"}

    def run_clustering(
        self,
        spatial_eps_m: Optional[float] = None,
        min_samples: Optional[int] = None,
        temporal_days: Optional[int] = None,
    ) -> dict:
        spatial_eps = spatial_eps_m or settings.CLUSTERING_SPATIAL_EPS_METERS
        min_samp = min_samples or settings.CLUSTERING_MIN_SAMPLES
        temp_days = temporal_days or settings.CLUSTERING_TEMPORAL_DAYS

        logger.info(f"Running custom clustering: eps={spatial_eps}m, min_samples={min_samp}, temporal_window={temp_days}d")

        complaints = self.db.query(Complaint).filter(
            Complaint.latitude.isnot(None),
            Complaint.longitude.isnot(None),
            Complaint.cluster_id.is_(None)
        ).all()

        if len(complaints) < min_samp:
            return {
                "total_complaints": len(complaints),
                "total_clusters": 0,
                "unclustered_complaints": len(complaints),
                "clusters": [],
                "algorithm": "CompositeAffinity+DBSCAN",
                "parameters": {"spatial_eps_m": spatial_eps, "min_samples": min_samp, "temporal_days": temp_days},
            }

        # 1. Semantic Similarity Matrix (TF-IDF)
        texts = [c.description or "" for c in complaints]
        tfidf_sims = np.zeros((len(complaints), len(complaints)))
        if any(texts):
            try:
                vectorizer = TfidfVectorizer(max_features=1000, stop_words="english", min_df=1)
                tfidf_sims = cosine_similarity(vectorizer.fit_transform(texts))
            except Exception as e:
                logger.warning(f"TF-IDF failed: {e}")

        # 2. Build Distance Matrix based on Relationship Score
        N = len(complaints)
        distance_matrix = np.zeros((N, N))
        pairwise_evidence = {}

        for i in range(N):
            for j in range(i + 1, N):
                rel = self._compute_relationship(complaints[i], complaints[j], tfidf_sims[i, j], spatial_eps, temp_days)
                dist = 1.0 - rel["total"]
                distance_matrix[i, j] = dist
                distance_matrix[j, i] = dist
                pairwise_evidence[(i, j)] = rel
                pairwise_evidence[(j, i)] = rel
            distance_matrix[i, i] = 0.0

        # 3. Cluster using DBSCAN with precomputed distances
        # Relationship threshold: we want things connected if total rel > 0.4
        # So distance < 0.6
        dbscan = DBSCAN(eps=0.6, min_samples=min_samp, metric='precomputed')
        labels = dbscan.fit_predict(distance_matrix)

        # 4. Create clusters
        clusters_created = []
        unique_labels = set(labels)
        unique_labels.discard(-1)

        for cluster_label in sorted(unique_labels):
            member_indices = [i for i, l in enumerate(labels) if l == cluster_label]
            if len(member_indices) < min_samp:
                continue
                
            member_complaints = [complaints[i] for i in member_indices]
            cluster = self._create_cluster(
                member_complaints,
                member_indices,
                pairwise_evidence,
                cluster_label
            )
            clusters_created.append(cluster)

        unclustered = sum(1 for l in labels if l == -1)
        self.db.commit()

        result = {
            "total_complaints": len(complaints),
            "total_clusters": len(clusters_created),
            "unclustered_complaints": unclustered,
            "clusters": clusters_created,
            "algorithm": "CompositeAffinity+DBSCAN",
            "parameters": {"spatial_eps_m": spatial_eps, "min_samples": min_samp, "temporal_days": temp_days},
        }
        return result

    def _compute_relationship(self, c1: Complaint, c2: Complaint, tfidf_sim: float, max_dist: float, max_days: int) -> dict:
        dist_m = haversine(c1.latitude, c1.longitude, c2.latitude, c2.longitude)
        if dist_m > max_dist * 2: # Hard cutoff
            return {"total": 0.0, "spatial": 0.0, "temporal": 0.0, "semantic": 0.0, "infrastructure": 0.0}
            
        spatial_score = max(0, 1.0 - (dist_m / max_dist))

        if c1.reported_at and c2.reported_at:
            days = abs((c1.reported_at - c2.reported_at).total_seconds()) / 86400.0
            if days > max_days:
                return {"total": 0.0, "spatial": 0.0, "temporal": 0.0, "semantic": 0.0, "infrastructure": 0.0}
            temporal_score = max(0, 1.0 - (days / max_days))
        else:
            temporal_score = 0.5

        cat1 = (c1.category or c1.incident_type).upper()
        cat2 = (c2.category or c2.incident_type).upper()

        infra_score = 0.0
        if cat1 == cat2:
            sem_score = 1.0
            infra_score = 1.0
        elif cat1 in self.chain_water and cat2 in self.chain_water:
            sem_score = 0.8
            infra_score = 0.8
        elif cat1 in self.chain_road and cat2 in self.chain_road:
            sem_score = 0.8
            infra_score = 0.8
        elif cat1 in self.chain_light and cat2 in self.chain_light:
            sem_score = 0.8
            infra_score = 0.8
        else:
            sem_score = float(tfidf_sim)
            if sem_score < 0.2:
                # Different chains AND low text similarity -> Unrelated, do not merge!
                return {"total": 0.0, "spatial": spatial_score, "temporal": temporal_score, "semantic": sem_score, "infrastructure": 0.0}
            infra_score = 0.2

        total = (0.4 * spatial_score) + (0.3 * temporal_score) + (0.2 * sem_score) + (0.1 * infra_score)

        return {
            "total": float(total),
            "spatial": float(spatial_score),
            "temporal": float(temporal_score),
            "semantic": float(sem_score),
            "infrastructure": float(infra_score)
        }

    def _create_cluster(
        self,
        member_complaints: list[Complaint],
        member_indices: list[int],
        pairwise_evidence: dict,
        cluster_label: int,
    ) -> FailureCluster:
        centroid_lat, centroid_lon = self.geo_service.compute_centroid(member_complaints)
        spatial_radius = self.geo_service.compute_spatial_radius(member_complaints, (centroid_lat, centroid_lon))

        dates = sorted([c.reported_at for c in member_complaints if c.reported_at])
        time_start = dates[0] if dates else None
        time_end = dates[-1] if dates else None

        incident_episodes = 0
        if dates:
            incident_episodes = 1
            current_episode_start = dates[0]
            for dt in dates[1:]:
                if (dt - current_episode_start).total_seconds() > 48 * 3600:
                    incident_episodes += 1
                    current_episode_start = dt

        categories = list(set(c.category or c.incident_type for c in member_complaints))
        severity_dist = dict(Counter(c.severity for c in member_complaints))

        spatials, temporals, semantics, infras = [], [], [], []
        if len(member_indices) >= 2:
            for i in range(len(member_indices)):
                for j in range(i + 1, len(member_indices)):
                    idx1 = member_indices[i]
                    idx2 = member_indices[j]
                    ev = pairwise_evidence.get((idx1, idx2), {})
                    if ev:
                        spatials.append(ev.get("spatial", 0.0))
                        temporals.append(ev.get("temporal", 0.0))
                        semantics.append(ev.get("semantic", 0.0))
                        infras.append(ev.get("infrastructure", 0.0))

        avg_spatial = float(np.mean(spatials)) if spatials else 1.0
        avg_temporal = float(np.mean(temporals)) if temporals else 1.0
        avg_semantic = float(np.mean(semantics)) if semantics else 1.0
        avg_infra = float(np.mean(infras)) if infras else 1.0

        relationship_evidence = {
            "spatial": round(avg_spatial, 3),
            "temporal": round(avg_temporal, 3),
            "semantic": round(avg_semantic, 3),
            "event": "Correlated based on 48h windows" if incident_episodes < len(member_complaints) else "Distinct independent events",
            "infrastructure": round(avg_infra, 3)
        }

        # Calculate confidence
        base_confidence = (0.35 * avg_spatial) + (0.30 * avg_semantic) + (0.25 * avg_temporal) + (0.10 * avg_infra)
        confidence = min(0.99, base_confidence + (min(20, len(member_complaints)) * 0.01))

        if confidence < 0.45:
            conf_level = "LOW"
            evidence_strength = "WEAK"
        elif confidence < 0.75:
            conf_level = "MODERATE"
            evidence_strength = "MODERATE"
        else:
            conf_level = "HIGH"
            evidence_strength = "STRONG"

        primary_category = max(
            Counter(c.category or c.incident_type for c in member_complaints).items(),
            key=lambda x: x[1],
        )[0] if member_complaints else "Unknown"

        ward = member_complaints[0].ward if member_complaints and member_complaints[0].ward else "Unknown"
        title = f"{primary_category.replace('_', ' ').title()} Cluster - {ward}"

        rationale = (
            f"Clustered {len(member_complaints)} complaints based on multi-signal evidence. "
            f"Strongest signals: "
        )
        signals = []
        if avg_spatial > 0.6: signals.append("spatial proximity")
        if avg_semantic > 0.6: signals.append("category/semantic relationship")
        if avg_temporal > 0.6: signals.append("temporal coherence")
        rationale += ", ".join(signals) + f". {incident_episodes} distinct incident episodes identified."

        site = self.geo_service.find_or_create_site(centroid_lat, centroid_lon, ward=ward)

        cluster = FailureCluster(
            title=title,
            complaint_count=len(member_complaints),
            incident_count=incident_episodes,
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
            semantic_similarity=round(avg_semantic, 3),
            cluster_rationale=rationale,
            relationship_evidence=relationship_evidence,
            confidence_level=conf_level,
            evidence_strength=evidence_strength,
            data_truth=DataTruth.MODEL_ESTIMATION.value,
        )
        self.db.add(cluster)
        self.db.flush()

        for complaint in member_complaints:
            complaint.cluster_id = cluster.cluster_id
            complaint.status = ComplaintStatus.CLUSTERED.value

        return cluster

    def get_clusters(self) -> list[FailureCluster]:
        return self.db.query(FailureCluster).order_by(FailureCluster.complaint_count.desc()).all()

    def get_cluster(self, cluster_id: str) -> Optional[FailureCluster]:
        return self.db.query(FailureCluster).filter(FailureCluster.cluster_id == cluster_id).first()

    def get_cluster_complaints(self, cluster_id: str) -> list[Complaint]:
        return self.db.query(Complaint).filter(Complaint.cluster_id == cluster_id).all()
