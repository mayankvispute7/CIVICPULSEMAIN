"""
Geospatial Service.

Handles:
- Site creation and lookup
- Spatial proximity queries
- Nearby complaint search
- Site context at multiple levels (SITE, LOCAL, CATCHMENT, CORRIDOR, WARD, CITY)
- Infrastructure proximity (synthetic for demo)
"""

import math
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.domain import Site, Complaint, FailureCluster, HistoricalIncident
from app.models.enums import DataTruth

logger = logging.getLogger(__name__)

# Approximate conversion: 1 degree latitude ~ 111,320 meters
DEG_TO_METERS = 111320.0
SITE_MERGE_RADIUS_M = 50.0  # complaints within 50m share a site


class GeospatialService:
    """Service for geospatial operations."""

    def __init__(self, db: Session):
        self.db = db

    def find_or_create_site(
        self,
        latitude: float,
        longitude: float,
        ward: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Site:
        """
        Find existing site within merge radius or create a new one.
        Complaints within ~50m of each other share the same site.
        """
        radius_deg = SITE_MERGE_RADIUS_M / DEG_TO_METERS

        existing = self.db.query(Site).filter(
            Site.latitude.between(latitude - radius_deg, latitude + radius_deg),
            Site.longitude.between(longitude - radius_deg, longitude + radius_deg),
        ).first()

        if existing:
            return existing

        # Create new site
        label = address or f"Site at ({latitude:.4f}, {longitude:.4f})"
        if ward:
            label = f"{ward} - {label}"

        site = Site(
            site_label=label,
            latitude=latitude,
            longitude=longitude,
            ward=ward,
            data_truth=DataTruth.SYNTHETIC_DATA.value,
        )
        self.db.add(site)
        self.db.flush()
        return site

    def find_nearby_complaints(
        self,
        latitude: float,
        longitude: float,
        radius_m: float = 250.0,
    ) -> list[Complaint]:
        """Find complaints within radius_m meters of a point."""
        radius_deg = radius_m / DEG_TO_METERS
        return self.db.query(Complaint).filter(
            Complaint.latitude.isnot(None),
            Complaint.longitude.isnot(None),
            Complaint.latitude.between(latitude - radius_deg, latitude + radius_deg),
            Complaint.longitude.between(longitude - radius_deg, longitude + radius_deg),
        ).all()

    def find_nearby_sites(
        self,
        latitude: float,
        longitude: float,
        radius_m: float = 500.0,
    ) -> list[Site]:
        """Find sites within radius_m meters of a point."""
        radius_deg = radius_m / DEG_TO_METERS
        return self.db.query(Site).filter(
            Site.latitude.between(latitude - radius_deg, latitude + radius_deg),
            Site.longitude.between(longitude - radius_deg, longitude + radius_deg),
        ).all()

    def get_site_context(self, site_id: str, level: str = "SITE") -> dict:
        """
        Get progressive spatial context for a site.

        Levels: SITE (50m), LOCAL (250m), CATCHMENT (1000m), CORRIDOR (2000m), WARD, CITY
        """
        site = self.db.query(Site).filter(Site.site_id == site_id).first()
        if not site:
            return {}

        radius_map = {
            "SITE": 50.0,
            "LOCAL": 250.0,
            "CATCHMENT": 1000.0,
            "CORRIDOR": 2000.0,
            "WARD": 5000.0,
            "CITY": 50000.0,
        }
        radius = radius_map.get(level, 250.0)

        nearby_complaints = self.find_nearby_complaints(site.latitude, site.longitude, radius)

        # Generate synthetic infrastructure context for demo
        infrastructure = self._get_demo_infrastructure(site, radius)

        context = {
            "site": site,
            "level": level,
            "radius_m": radius,
            "nearby_complaints": nearby_complaints,
            "nearby_infrastructure": infrastructure.get("infrastructure", []),
            "terrain_context": infrastructure.get("terrain", None),
            "drainage_context": infrastructure.get("drainage", None),
            "building_count": infrastructure.get("building_count", 0),
            "critical_facilities": infrastructure.get("critical_facilities", []),
        }

        # Add historical incidents at site
        if level in ("LOCAL", "CATCHMENT", "CORRIDOR", "WARD", "CITY"):
            incidents = self.db.query(HistoricalIncident).filter(
                HistoricalIncident.site_id == site_id
            ).all()
            context["historical_incidents"] = incidents

        return context

    def _get_demo_infrastructure(self, site: Site, radius_m: float) -> dict:
        """Generate demo infrastructure context."""
        return {
            "infrastructure": [
                {
                    "type": "drain",
                    "id": f"DRAIN-{site.site_id[:8]}",
                    "name": f"Storm drain near {site.site_label}",
                    "distance_m": round(radius_m * 0.3, 1),
                    "capacity": "600mm diameter",
                    "condition": "Partially blocked",
                    "data_truth": DataTruth.SYNTHETIC_DATA.value,
                },
                {
                    "type": "road",
                    "id": f"ROAD-{site.site_id[:8]}",
                    "name": f"Road segment near {site.site_label}",
                    "distance_m": round(radius_m * 0.1, 1),
                    "classification": "Secondary road",
                    "data_truth": DataTruth.SYNTHETIC_DATA.value,
                },
            ],
            "terrain": {
                "elevation_m": 560 + (hash(site.site_id) % 40),
                "slope_pct": round(1.5 + (hash(site.site_id) % 5) * 0.5, 1),
                "depression": hash(site.site_id) % 3 == 0,
                "data_truth": DataTruth.SYNTHETIC_DATA.value,
            },
            "drainage": {
                "nearest_drain_m": round(radius_m * 0.3, 1),
                "drainage_direction": "NW to SE",
                "estimated_capacity_m3s": round(0.5 + (hash(site.site_id) % 10) * 0.1, 2),
                "data_truth": DataTruth.SYNTHETIC_DATA.value,
            },
            "building_count": 15 + (hash(site.site_id) % 30),
            "critical_facilities": [
                {
                    "type": "hospital" if hash(site.site_id) % 4 == 0 else "school",
                    "name": f"Facility near {site.site_label}",
                    "distance_m": round(200 + (hash(site.site_id) % 300), 0),
                    "data_truth": DataTruth.SYNTHETIC_DATA.value,
                }
            ] if hash(site.site_id) % 3 == 0 else [],
        }

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters using Haversine formula."""
        R = 6371000  # Earth's radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def compute_centroid(self, complaints: list[Complaint]) -> tuple[float, float]:
        """Compute centroid of a list of complaints."""
        lats = [c.latitude for c in complaints if c.latitude is not None]
        lons = [c.longitude for c in complaints if c.longitude is not None]
        if not lats or not lons:
            return 0.0, 0.0
        return sum(lats) / len(lats), sum(lons) / len(lons)

    def compute_spatial_radius(self, complaints: list[Complaint], centroid: tuple[float, float]) -> float:
        """Compute maximum distance from centroid to any complaint in meters."""
        max_dist = 0.0
        for c in complaints:
            if c.latitude is not None and c.longitude is not None:
                d = self.haversine_distance(centroid[0], centroid[1], c.latitude, c.longitude)
                max_dist = max(max_dist, d)
        return max_dist
