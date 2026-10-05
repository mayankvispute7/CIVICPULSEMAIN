"""
Failure Analysis Service.

Handles:
- Failure case creation from clusters
- Failure fingerprint generation
- Failure chain construction
- Root-cause hypothesis generation
- Evidence aggregation
- Historical incident integration
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.domain import (
    FailureCase, FailureCluster, Evidence, FailureHypothesis,
    HistoricalIncident, Complaint, Site
)
from app.models.enums import (
    CaseStatus, EvidenceType, HypothesisStatus, DataTruth, FailureType
)

logger = logging.getLogger(__name__)

# Mapping of categories to failure types
CATEGORY_TO_FAILURE = {
    "WATERLOGGING": FailureType.WATERLOGGING.value,
    "FLOODING": FailureType.WATERLOGGING.value,
    "DRAINAGE": FailureType.DRAINAGE_FAILURE.value,
    "DRAIN_OVERFLOW": FailureType.DRAINAGE_FAILURE.value,
    "POTHOLE": FailureType.ROAD_DAMAGE.value,
    "ROAD_DAMAGE": FailureType.ROAD_DAMAGE.value,
    "ROAD_CAVE_IN": FailureType.ROAD_DAMAGE.value,
    "SEWAGE": FailureType.SEWAGE_OVERFLOW.value,
    "MANHOLE": FailureType.SEWAGE_OVERFLOW.value,
    "STRUCTURAL": FailureType.STRUCTURAL_DAMAGE.value,
}


class FailureAnalysisService:
    """Service for failure case analysis and fingerprinting."""

    def __init__(self, db: Session):
        self.db = db

    def create_case_from_cluster(self, cluster_id: str) -> Optional[FailureCase]:
        """Create a failure case from a confirmed cluster."""
        cluster = self.db.query(FailureCluster).filter(
            FailureCluster.cluster_id == cluster_id
        ).first()

        if not cluster:
            logger.error(f"Cluster not found: {cluster_id}")
            return None

        # Determine failure type from categories
        failure_type = FailureType.OTHER.value
        if cluster.categories:
            for cat in cluster.categories:
                if cat.upper() in CATEGORY_TO_FAILURE:
                    failure_type = CATEGORY_TO_FAILURE[cat.upper()]
                    break

        # Get complaints for impact summary
        complaints = self.db.query(Complaint).filter(
            Complaint.cluster_id == cluster_id
        ).all()

        impact_summary = (
            f"{len(complaints)} complaints over "
            f"{cluster.spatial_radius_m:.0f}m area. "
            f"Categories: {', '.join(cluster.categories or [])}. "
            f"Severity distribution: {cluster.severity_distribution}."
        )

        case = FailureCase(
            cluster_id=cluster_id,
            site_id=cluster.site_id,
            title=cluster.title.replace("Cluster", "Case"),
            failure_type=failure_type,
            recurrence_count=0,
            impact_summary=impact_summary,
            confidence=cluster.confidence,
            status=CaseStatus.INVESTIGATING.value,
            data_truth=DataTruth.MODEL_ESTIMATION.value,
        )
        self.db.add(case)
        self.db.flush()

        # Generate evidence
        self._generate_evidence(case, complaints, cluster)

        # Generate fingerprint
        fingerprint = self._generate_fingerprint(case, complaints, cluster)
        case.fingerprint = fingerprint

        # Generate failure chain
        failure_chain = self._generate_failure_chain(case, failure_type)
        case.failure_chain = failure_chain

        # Generate hypotheses
        self._generate_hypotheses(case, complaints, cluster)

        # Generate historical incidents (demo)
        self._generate_historical_incidents(case, cluster)

        # Update cluster status
        cluster.status = "CASE_CREATED"

        self.db.commit()
        logger.info(f"Created failure case {case.case_id} from cluster {cluster_id}")
        return case

    def _generate_evidence(
        self,
        case: FailureCase,
        complaints: list[Complaint],
        cluster: FailureCluster,
    ):
        """Generate evidence records for a failure case."""
        # Complaint evidence
        ev_complaint = Evidence(
            case_id=case.case_id,
            type=EvidenceType.COMPLAINT.value,
            title=f"Complaint cluster: {len(complaints)} reports",
            source="CSV Import",
            description=f"{len(complaints)} citizen complaints reporting similar issues in the area.",
            value={
                "complaint_count": len(complaints),
                "categories": cluster.categories,
                "severity_distribution": cluster.severity_distribution,
            },
            confidence=0.9,
            timestamp=cluster.time_range_start,
            date_range_start=cluster.time_range_start,
            date_range_end=cluster.time_range_end,
            latitude=cluster.centroid_lat,
            longitude=cluster.centroid_lon,
            provenance={"source": "Civic Pulse CSV Import", "method": "DBSCAN clustering"},
            data_truth=DataTruth.EVIDENCE.value,
        )
        self.db.add(ev_complaint)

        # Rainfall evidence (synthetic for demo)
        ev_rainfall = Evidence(
            case_id=case.case_id,
            type=EvidenceType.RAINFALL.value,
            title="Rainfall correlation analysis",
            source="Weather data (synthetic)",
            description="Rainfall events correlated with complaint timing suggest weather-triggered infrastructure stress.",
            value={
                "correlated_events": 4,
                "avg_rainfall_mm": 65.0,
                "max_rainfall_mm": 112.0,
                "correlation_strength": 0.78,
            },
            confidence=0.75,
            latitude=cluster.centroid_lat,
            longitude=cluster.centroid_lon,
            provenance={"source": "Synthetic weather data", "method": "Temporal correlation"},
            assumptions=["Gridded rainfall data used, not station-level"],
            limitations=["Spatial resolution limited to ~10km grid"],
            data_truth=DataTruth.SYNTHETIC_DATA.value,
        )
        self.db.add(ev_rainfall)

        # Terrain evidence (synthetic)
        ev_terrain = Evidence(
            case_id=case.case_id,
            type=EvidenceType.TERRAIN.value,
            title="Terrain analysis",
            source="DEM analysis (synthetic)",
            description="Local terrain indicates depression or low-gradient area susceptible to water accumulation.",
            value={
                "elevation_m": 560,
                "local_slope_pct": 1.8,
                "depression_detected": True,
                "catchment_area_sqm": 45000,
            },
            confidence=0.7,
            latitude=cluster.centroid_lat,
            longitude=cluster.centroid_lon,
            provenance={"source": "Synthetic DEM analysis"},
            assumptions=["DEM resolution ~30m, not survey-grade"],
            data_truth=DataTruth.SYNTHETIC_DATA.value,
        )
        self.db.add(ev_terrain)

        # Drainage evidence (synthetic)
        ev_drainage = Evidence(
            case_id=case.case_id,
            type=EvidenceType.DRAINAGE.value,
            title="Drainage capacity screening",
            source="Screening model (synthetic)",
            description="Screening-level analysis suggests drainage capacity may be insufficient for moderate to heavy rainfall events.",
            value={
                "estimated_drain_capacity_m3s": 0.8,
                "estimated_demand_m3s": 1.2,
                "capacity_ratio": 0.67,
                "blockage_factor": 0.3,
                "effective_capacity_m3s": 0.56,
            },
            confidence=0.65,
            latitude=cluster.centroid_lat,
            longitude=cluster.centroid_lon,
            provenance={"source": "Screening-level model", "method": "Rational method"},
            assumptions=[
                "Drain dimensions estimated from typical municipal standards",
                "Blockage factor assumed at 30%",
                "Runoff coefficient assumed at 0.75 for urban area",
            ],
            limitations=[
                "Not calibrated against flood-depth observations",
                "Actual drain conditions unknown",
            ],
            data_truth=DataTruth.MODEL_ESTIMATION.value,
        )
        self.db.add(ev_drainage)

        self.db.flush()

    def _generate_fingerprint(
        self,
        case: FailureCase,
        complaints: list[Complaint],
        cluster: FailureCluster,
    ) -> dict:
        """Generate a structured failure fingerprint."""
        return {
            "case_id": case.case_id,
            "failure_type": case.failure_type,
            "complaint_count": len(complaints),
            "recurrence_count": case.recurrence_count,
            "spatial_extent_m": cluster.spatial_radius_m,
            "temporal_span_days": (
                (cluster.time_range_end - cluster.time_range_start).days
                if cluster.time_range_start and cluster.time_range_end else 0
            ),
            "rainfall_correlation": {
                "correlated_events": 4,
                "correlation_strength": 0.78,
                "data_truth": DataTruth.SYNTHETIC_DATA.value,
            },
            "terrain": {
                "depression_detected": True,
                "slope_pct": 1.8,
                "data_truth": DataTruth.SYNTHETIC_DATA.value,
            },
            "drainage": {
                "capacity_ratio": 0.67,
                "blockage_factor": 0.3,
                "data_truth": DataTruth.MODEL_ESTIMATION.value,
            },
            "hypothesis_confidence": cluster.confidence,
            "summary": (
                f"Evidence suggests a {case.failure_type.lower().replace('_', ' ')} pattern "
                f"with {len(complaints)} complaints. "
                f"Drainage capacity/connectivity constraint combined with "
                f"local terrain accumulation is the primary hypothesis."
            ),
            "evidence_strength": "MODERATE",
            "data_truth": DataTruth.MODEL_ESTIMATION.value,
        }

    def _generate_failure_chain(self, case: FailureCase, failure_type: str) -> list[dict]:
        """Generate a structured failure mechanism chain."""
        if failure_type in (FailureType.WATERLOGGING.value, FailureType.DRAINAGE_FAILURE.value):
            return [
                {"step": 1, "node": "Heavy Rainfall", "type": "trigger",
                 "evidence_supported": True, "confidence": 0.78,
                 "data_truth": DataTruth.SYNTHETIC_DATA.value},
                {"step": 2, "node": "High Runoff", "type": "mechanism",
                 "evidence_supported": True, "confidence": 0.7,
                 "data_truth": DataTruth.MODEL_ESTIMATION.value},
                {"step": 3, "node": "Terrain Depression", "type": "condition",
                 "evidence_supported": True, "confidence": 0.7,
                 "data_truth": DataTruth.SYNTHETIC_DATA.value},
                {"step": 4, "node": "Drainage Bottleneck", "type": "mechanism",
                 "evidence_supported": True, "confidence": 0.65,
                 "data_truth": DataTruth.MODEL_ESTIMATION.value},
                {"step": 5, "node": "Water Accumulation", "type": "effect",
                 "evidence_supported": True, "confidence": 0.8,
                 "data_truth": DataTruth.EVIDENCE.value},
                {"step": 6, "node": "Road Disruption", "type": "impact",
                 "evidence_supported": True, "confidence": 0.85,
                 "data_truth": DataTruth.EVIDENCE.value},
                {"step": 7, "node": "Multiple Complaints", "type": "observation",
                 "evidence_supported": True, "confidence": 0.95,
                 "data_truth": DataTruth.EVIDENCE.value},
            ]
        elif failure_type in (FailureType.ROAD_DAMAGE.value,):
            return [
                {"step": 1, "node": "Heavy Traffic / Rainfall", "type": "trigger",
                 "evidence_supported": True, "confidence": 0.7},
                {"step": 2, "node": "Sub-surface Water Ingress", "type": "mechanism",
                 "evidence_supported": False, "confidence": 0.5},
                {"step": 3, "node": "Pavement Deterioration", "type": "mechanism",
                 "evidence_supported": True, "confidence": 0.75},
                {"step": 4, "node": "Pothole / Surface Failure", "type": "effect",
                 "evidence_supported": True, "confidence": 0.85},
                {"step": 5, "node": "Vehicle Damage / Safety Risk", "type": "impact",
                 "evidence_supported": True, "confidence": 0.8},
                {"step": 6, "node": "Multiple Complaints", "type": "observation",
                 "evidence_supported": True, "confidence": 0.95},
            ]
        else:
            return [
                {"step": 1, "node": "Infrastructure Stress", "type": "trigger",
                 "evidence_supported": False, "confidence": 0.5},
                {"step": 2, "node": "Component Failure", "type": "mechanism",
                 "evidence_supported": False, "confidence": 0.5},
                {"step": 3, "node": "Service Disruption", "type": "effect",
                 "evidence_supported": True, "confidence": 0.7},
                {"step": 4, "node": "Multiple Complaints", "type": "observation",
                 "evidence_supported": True, "confidence": 0.95},
            ]

    def _generate_hypotheses(
        self,
        case: FailureCase,
        complaints: list[Complaint],
        cluster: FailureCluster,
    ):
        """Generate failure hypotheses based on evidence."""
        evidence = self.db.query(Evidence).filter(Evidence.case_id == case.case_id).all()
        evidence_ids = [e.evidence_id for e in evidence]

        if case.failure_type in (FailureType.WATERLOGGING.value, FailureType.DRAINAGE_FAILURE.value):
            h1 = FailureHypothesis(
                case_id=case.case_id,
                title="Drainage capacity/connectivity constraint",
                description=(
                    "Evidence suggests that the existing drainage infrastructure has "
                    "insufficient capacity or connectivity to handle moderate to heavy "
                    "rainfall events, leading to recurring waterlogging."
                ),
                confidence=0.82,
                status=HypothesisStatus.SUPPORTED.value,
                evidence_ids=evidence_ids,
                mechanism=(
                    "Heavy rainfall → high runoff → drainage demand exceeds capacity → "
                    "water accumulation → road/area disruption"
                ),
                assumptions=[
                    "Drain capacity estimated from typical municipal standards",
                    "Blockage factor estimated, not field-verified",
                ],
                limitations=[
                    "Actual drain dimensions not confirmed by field survey",
                    "Upstream/downstream connectivity not fully mapped",
                ],
                data_truth=DataTruth.MODEL_ESTIMATION.value,
            )
            self.db.add(h1)

            h2 = FailureHypothesis(
                case_id=case.case_id,
                title="Terrain-induced accumulation",
                description=(
                    "Local terrain depression creates a natural accumulation point "
                    "where runoff concentrates, exacerbating drainage stress."
                ),
                confidence=0.68,
                status=HypothesisStatus.PARTIALLY_SUPPORTED.value,
                evidence_ids=[e.evidence_id for e in evidence if e.type == EvidenceType.TERRAIN.value],
                mechanism="Terrain depression → runoff concentration → prolonged ponding",
                assumptions=["DEM resolution sufficient for local depression detection"],
                limitations=["DEM resolution ~30m, micro-topography not captured"],
                data_truth=DataTruth.MODEL_ESTIMATION.value,
            )
            self.db.add(h2)
        else:
            h1 = FailureHypothesis(
                case_id=case.case_id,
                title="Infrastructure degradation",
                description=(
                    "Evidence suggests progressive degradation of infrastructure "
                    "components leading to recurring service failure."
                ),
                confidence=0.7,
                status=HypothesisStatus.PROPOSED.value,
                evidence_ids=evidence_ids,
                data_truth=DataTruth.MODEL_ESTIMATION.value,
            )
            self.db.add(h1)

        self.db.flush()

    def _generate_historical_incidents(self, case: FailureCase, cluster: FailureCluster):
        """Generate synthetic historical incidents for demo."""
        from datetime import timedelta
        import random

        random.seed(hash(case.case_id) % 2**32)

        base_date = cluster.time_range_start or datetime(2026, 7, 1)

        incidents = [
            {
                "title": f"Previous {case.failure_type.lower().replace('_', ' ')} incident",
                "description": "Similar waterlogging/infrastructure issue reported in the same area.",
                "occurred_at": base_date - timedelta(days=random.randint(180, 365)),
                "intervention_taken": "Drain cleaning",
                "intervention_outcome": "Temporary relief, recurrence after 3 months",
                "recurrence_after_days": 90,
            },
            {
                "title": f"Earlier {case.failure_type.lower().replace('_', ' ')} incident",
                "occurred_at": base_date - timedelta(days=random.randint(400, 600)),
                "intervention_taken": "Debris removal and minor repair",
                "intervention_outcome": "Partial improvement, problem persisted during heavy rain",
                "recurrence_after_days": 120,
            },
            {
                "title": f"Historical {case.failure_type.lower().replace('_', ' ')} report",
                "occurred_at": base_date - timedelta(days=random.randint(700, 900)),
                "intervention_taken": "Emergency pumping",
                "intervention_outcome": "Immediate relief only, no lasting improvement",
                "recurrence_after_days": 45,
            },
            {
                "title": f"Monsoon season {case.failure_type.lower().replace('_', ' ')}",
                "occurred_at": base_date - timedelta(days=random.randint(365, 730)),
                "intervention_taken": "Desilting of drains",
                "intervention_outcome": "Moderate improvement for one season",
                "recurrence_after_days": 180,
            },
        ]

        for inc_data in incidents:
            incident = HistoricalIncident(
                case_id=case.case_id,
                site_id=case.site_id,
                title=inc_data["title"],
                description=inc_data.get("description", ""),
                incident_type=case.failure_type,
                occurred_at=inc_data["occurred_at"],
                severity="HIGH",
                intervention_taken=inc_data.get("intervention_taken"),
                intervention_outcome=inc_data.get("intervention_outcome"),
                recurrence_after_days=inc_data.get("recurrence_after_days"),
                data_truth=DataTruth.SYNTHETIC_DATA.value,
            )
            self.db.add(incident)

        case.recurrence_count = len(incidents)
        self.db.flush()

    # ─────────────────────────────────────────────────────────
    # Query methods
    # ─────────────────────────────────────────────────────────

    def get_cases(self) -> list[FailureCase]:
        return self.db.query(FailureCase).order_by(FailureCase.created_at.desc()).all()

    def get_case(self, case_id: str) -> Optional[FailureCase]:
        # Try finding by case_id first
        case = self.db.query(FailureCase).filter(FailureCase.case_id == case_id).first()
        if case:
            return case
        # If not found, try finding by cluster_id (since frontend routes using cluster_id)
        return self.db.query(FailureCase).filter(FailureCase.cluster_id == case_id).first()

    def get_case_evidence(self, case_id: str) -> list[Evidence]:
        return self.db.query(Evidence).filter(Evidence.case_id == case_id).all()

    def get_case_hypotheses(self, case_id: str) -> list[FailureHypothesis]:
        return self.db.query(FailureHypothesis).filter(
            FailureHypothesis.case_id == case_id
        ).all()

    def get_case_history(self, case_id: str) -> dict:
        case = self.get_case(case_id)
        if not case:
            return {}

        incidents = self.db.query(HistoricalIncident).filter(
            HistoricalIncident.case_id == case_id
        ).order_by(HistoricalIncident.occurred_at.desc()).all()

        previous_complaints = self.db.query(Complaint).filter(
            Complaint.cluster_id == case.cluster_id
        ).all()

        recurrence_intervals = [
            i.recurrence_after_days for i in incidents
            if i.recurrence_after_days is not None
        ]

        return {
            "case_id": case_id,
            "site_id": case.site_id,
            "historical_incidents": incidents,
            "previous_complaints": previous_complaints,
            "recurrence_intervals": recurrence_intervals,
            "total_past_incidents": len(incidents),
            "total_previous_interventions": sum(
                1 for i in incidents if i.intervention_taken
            ),
        }

    def create_cases_from_all_clusters(self) -> list[FailureCase]:
        """Create failure cases from all confirmed clusters that don't have cases yet."""
        clusters = self.db.query(FailureCluster).filter(
            FailureCluster.status != "CASE_CREATED"
        ).all()

        cases = []
        for cluster in clusters:
            case = self.create_case_from_cluster(cluster.cluster_id)
            if case:
                cases.append(case)

        return cases
