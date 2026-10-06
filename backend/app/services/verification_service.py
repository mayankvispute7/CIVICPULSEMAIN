"""
Verification Service.

Handles:
- Field evidence submission (photos, GPS)
- Integrity checks (location, timestamp, duplication, manipulation)
- Work order verification
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.domain import (
    FieldEvidence, Verification, WorkOrder, WorkOrderTask
)
from app.models.enums import (
    VerificationStatus, EvidenceConsistency, WorkOrderStatus
)

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for checking field evidence and verifying work execution."""

    def __init__(self, db: Session):
        self.db = db

    def submit_field_evidence(
        self,
        work_order_id: str,
        latitude: float,
        longitude: float,
        captured_at: datetime,
        task_id: Optional[str] = None,
        image_url: Optional[str] = None,
        metadata_info: Optional[dict] = None,
    ) -> Optional[FieldEvidence]:
        """Submit field evidence with integrity checks."""
        work_order = self.db.query(WorkOrder).filter(
            WorkOrder.work_order_id == work_order_id
        ).first()

        if not work_order:
            logger.error(f"Work order not found: {work_order_id}")
            return None

        # Perform integrity checks
        location_consistency, loc_dist = self._check_location(work_order, latitude, longitude)
        timestamp_consistency, time_diff = self._check_timestamp(captured_at)
        duplicate_sim, dup_check = self._check_duplicates(work_order_id, image_url)
        visual_change = self._evaluate_visual_change(image_url, metadata_info or {})
        manipulation = self._check_manipulation(metadata_info or {})

        # Compute overall consistency
        overall = EvidenceConsistency.MEDIUM.value
        if location_consistency == "MATCH" and timestamp_consistency == "PLAUSIBLE" and visual_change == "CONSISTENT_WITH_WORK" and not manipulation:
            overall = EvidenceConsistency.HIGH.value
        elif location_consistency == "MISMATCH" or timestamp_consistency == "IMPLAUSIBLE" or visual_change == "INCONSISTENT" or manipulation:
            overall = EvidenceConsistency.LOW.value

        evidence = FieldEvidence(
            work_order_id=work_order_id,
            task_id=task_id,
            captured_at=captured_at,
            latitude=latitude,
            longitude=longitude,
            image_url=image_url,
            metadata_info=metadata_info or {},
            location_consistency=location_consistency,
            timestamp_consistency=timestamp_consistency,
            duplicate_similarity=duplicate_sim,
            visual_change=visual_change,
            manipulation_indicators=manipulation,
            overall_consistency=overall,
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)

        return evidence

    def verify_work_order(
        self,
        work_order_id: str,
        verified_by: str,
    ) -> Optional[Verification]:
        """Perform verification on a completed work order."""
        work_order = self.db.query(WorkOrder).filter(
            WorkOrder.work_order_id == work_order_id
        ).first()

        if not work_order:
            return None

        # Get all evidence for this work order (only latest for demo re-upload purposes)
        evidence_list = self.db.query(FieldEvidence).filter(
            FieldEvidence.work_order_id == work_order_id
        ).order_by(FieldEvidence.captured_at.desc()).limit(1).all()

        checks = []
        confidence = 0.0
        status = VerificationStatus.PENDING.value
        overall_consistency = EvidenceConsistency.LOW.value
        manual_review = False
        review_reason = None

        if not evidence_list:
            checks.append("No field evidence submitted")
            status = VerificationStatus.REVIEW_REQUIRED.value
            manual_review = True
            review_reason = "Missing evidence"
        else:
            # Analyze evidence
            high_count = sum(1 for e in evidence_list if e.overall_consistency == EvidenceConsistency.HIGH.value)
            low_count = sum(1 for e in evidence_list if e.overall_consistency == EvidenceConsistency.LOW.value)
            
            checks.append(f"Analyzed {len(evidence_list)} evidence items")
            checks.append(f"{high_count} items with HIGH consistency")
            
            if low_count > 0:
                checks.append(f"{low_count} items with LOW consistency")
                status = VerificationStatus.REVIEW_REQUIRED.value
                manual_review = True
                review_reason = "Low consistency evidence detected (possible location/time mismatch or duplicate)"
                overall_consistency = EvidenceConsistency.LOW.value
                confidence = 0.3
            else:
                status = VerificationStatus.VERIFIED.value
                overall_consistency = EvidenceConsistency.HIGH.value if high_count > 0 else EvidenceConsistency.MEDIUM.value
                confidence = 0.85 + (0.1 if high_count > 0 else 0)

        # Check task completion
        tasks = self.db.query(WorkOrderTask).filter(
            WorkOrderTask.work_order_id == work_order_id
        ).all()
        
        incomplete = sum(1 for t in tasks if t.status not in ("COMPLETED", "SKIPPED", "CANCELLED"))
        if incomplete > 0:
            checks.append(f"{incomplete} tasks are not marked complete")
            if status != VerificationStatus.REVIEW_REQUIRED.value:
                status = VerificationStatus.REVIEW_REQUIRED.value
                manual_review = True
                review_reason = "Incomplete tasks"
                confidence = 0.2

        verification = Verification(
            work_order_id=work_order_id,
            status=status,
            overall_consistency=overall_consistency,
            checks=checks,
            evidence_ids=[e.evidence_id for e in evidence_list],
            confidence=confidence,
            manual_review_required=manual_review,
            review_reason=review_reason,
            verified_by=verified_by if status == VerificationStatus.VERIFIED.value else None,
            verified_at=datetime.utcnow() if status == VerificationStatus.VERIFIED.value else None,
        )
        self.db.add(verification)
        self.db.commit()

        return verification
        
    def manual_verify(
        self,
        verification_id: str,
        decision: str,
        reviewer_id: str,
        notes: str,
    ) -> Optional[Verification]:
        """Manually approve or reject a verification that required review."""
        verification = self.db.query(Verification).filter(
            Verification.verification_id == verification_id
        ).first()

        if not verification:
            return None

        if decision.upper() == "APPROVE":
            verification.status = VerificationStatus.VERIFIED.value
        else:
            verification.status = VerificationStatus.REJECTED.value
            
        verification.verified_by = reviewer_id
        verification.verified_at = datetime.utcnow()
        
        if not verification.checks:
            verification.checks = []
        verification.checks.append(f"Manual review: {decision} - {notes}")
        
        self.db.commit()
        return verification

    # ─────────────────────────────────────────────────────────
    # Integrity Helpers (Simulated for MVP)
    # ─────────────────────────────────────────────────────────

    def _check_location(self, work_order: WorkOrder, lat: float, lon: float) -> tuple[str, float]:
        """Check if evidence location matches work order location."""
        if not work_order.location_lat or not work_order.location_lon:
            return "UNKNOWN", 0.0
            
        # Haversine distance
        from app.services.geospatial_service import GeospatialService
        dist = GeospatialService.haversine_distance(
            work_order.location_lat, work_order.location_lon, lat, lon
        )
        
        if dist < 100:
            return "MATCH", dist
        elif dist < 500:
            return "PLAUSIBLE", dist
        else:
            return "MISMATCH", dist

    def _check_timestamp(self, captured_at: datetime) -> tuple[str, float]:
        """Check if timestamp is plausible (not in future, not too old)."""
        now = datetime.utcnow()
        if captured_at.tzinfo is not None:
            # Make now aware to match captured_at
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)
            
        if captured_at > now:
            return "IMPLAUSIBLE", 0.0  # Future
            
        diff_hours = (now - captured_at).total_seconds() / 3600
        if diff_hours < 24:
            return "PLAUSIBLE", diff_hours
        else:
            return "DELAYED", diff_hours

    def _check_duplicates(self, work_order_id: str, image_url: Optional[str]) -> tuple[float, str]:
        """Check for duplicated images."""
        if not image_url:
            return 0.0, "NO_IMAGE"
            
        # In a real system, this would use perceptual hashing (pHash) on the image.
        # For the hackathon MVP, we just return a low chance of duplication unless
        # the URLs are exactly identical.
        existing = self.db.query(FieldEvidence).filter(
            FieldEvidence.image_url == image_url,
            FieldEvidence.work_order_id != work_order_id
        ).first()
        
        if existing:
            return 1.0, "EXACT_DUPLICATE_URL"
            
        return 0.1, "UNIQUE"

    def _evaluate_visual_change(self, image_url: Optional[str], metadata_info: dict) -> str:
        """Simulate visual change evaluation."""
        if not image_url:
            return "UNKNOWN"
        
        # Mock logic: check filename from metadata for demo purposes
        filename = metadata_info.get("filename", "").lower()
        if "road" in filename or "satellite" in filename:
            return "CONSISTENT_WITH_WORK"
        
        # For demo: any other name means it's irrelevant (like a signature)
        if filename and filename != "unknown":
            return "INCONSISTENT"
            
        return "CONSISTENT_WITH_WORK"

    def _check_manipulation(self, metadata: dict) -> list[str]:
        """Simulate EXIF manipulation checks."""
        indicators = []
        if metadata.get("software") and "photoshop" in str(metadata.get("software")).lower():
            indicators.append("Editing software detected in EXIF")
        if metadata.get("original_date") != metadata.get("modify_date"):
            # Depending on the specific EXIF fields
            pass
        return indicators
        
    def get_verifications(self, work_order_id: str) -> list[Verification]:
        return self.db.query(Verification).filter(
            Verification.work_order_id == work_order_id
        ).order_by(Verification.created_at.desc()).all()
        
    def get_evidence(self, work_order_id: str) -> list[FieldEvidence]:
        return self.db.query(FieldEvidence).filter(
            FieldEvidence.work_order_id == work_order_id
        ).order_by(FieldEvidence.captured_at.desc()).all()
