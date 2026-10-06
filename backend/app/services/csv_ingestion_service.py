"""
CSV Ingestion Service.

Handles:
- CSV upload and parsing
- Schema validation (column names, types)
- Row-level validation (coordinates, timestamps, required fields)
- Duplicate detection
- Normalization
- Complaint creation
- Import summary generation
"""

import csv
import io
import hashlib
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.domain import CSVImport, Complaint, Site
from app.models.enums import ImportStatus, DataTruth, Severity, ComplaintStatus
from app.services.geospatial_service import GeospatialService

logger = logging.getLogger(__name__)

# Expected CSV columns (flexible — will map various column names)
COLUMN_MAPPINGS = {
    "complaint_id": ["complaint_id", "id", "complaint_no", "sr_no"],
    "date": ["date", "reported_at", "datetime", "timestamp", "date_time", "reported_date"],
    "description": ["description", "complaint_text", "text", "details", "complaint_description"],
    "address": ["address", "location", "location_address", "place"],
    "ward": ["ward", "ward_name", "ward_no", "zone"],
    "latitude": ["latitude", "lat", "y"],
    "longitude": ["longitude", "lon", "lng", "x"],
    "category": ["category", "incident_type", "type", "complaint_type", "complaint_category"],
    "severity": ["severity", "priority", "urgency"],
    "status": ["status", "complaint_status", "current_status"],
}

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_CATEGORIES = {
    "WATERLOGGING", "ROAD_DAMAGE", "DRAINAGE", "SEWAGE", "POTHOLE",
    "GARBAGE", "WATER_SUPPLY", "ELECTRICITY", "STRUCTURAL", "OTHER",
    "FLOODING", "DRAIN_OVERFLOW", "ROAD_CAVE_IN", "MANHOLE",
}


class CSVIngestionService:
    """Service for ingesting complaint data from CSV files."""

    def __init__(self, db: Session):
        self.db = db
        self.geo_service = GeospatialService(db)

    def ingest_csv(self, filename: str, content: bytes, data_truth: str = DataTruth.REAL_DATA.value) -> CSVImport:
        """
        Ingest a CSV file of complaints.

        Returns an import record with processing summary.
        """
        # Create import record
        csv_import = CSVImport(
            filename=filename,
            status=ImportStatus.PROCESSING.value,
            data_truth=data_truth,
        )
        self.db.add(csv_import)
        self.db.flush()

        logger.info(f"Starting CSV import: {filename} (import_id={csv_import.import_id})")

        try:
            # Parse CSV
            df = self._parse_csv(content)
            csv_import.total_rows = len(df)

            if len(df) == 0:
                csv_import.status = ImportStatus.FAILED.value
                csv_import.validation_errors = [{"error": "CSV file contains no data rows"}]
                csv_import.completed_at = datetime.utcnow()
                self.db.commit()
                return csv_import

            # Map columns
            df = self._map_columns(df)

            # Validate and process rows
            accepted = 0
            rejected = 0
            duplicates = 0
            errors = []
            seen_hashes = set()

            for idx, row in df.iterrows():
                row_num = idx + 2  # 1-indexed + header row
                row_errors = self._validate_row(row, row_num)

                if row_errors:
                    errors.extend(row_errors)
                    rejected += 1
                    continue

                # Duplicate detection
                row_hash = self._compute_row_hash(row)
                if row_hash in seen_hashes:
                    duplicates += 1
                    errors.append({
                        "row": row_num,
                        "field": "duplicate",
                        "error": "Duplicate complaint detected",
                    })
                    continue

                # Check DB duplicate
                if data_truth != DataTruth.SYNTHETIC_DATA.value and self._is_db_duplicate(row):
                    duplicates += 1
                    errors.append({
                        "row": row_num,
                        "field": "duplicate",
                        "error": "Complaint already exists in database",
                    })
                    continue

                seen_hashes.add(row_hash)

                # Create complaint
                try:
                    complaint = self._create_complaint(row, csv_import.import_id, data_truth)
                    self.db.add(complaint)
                    accepted += 1
                except Exception as e:
                    rejected += 1
                    errors.append({
                        "row": row_num,
                        "field": "creation",
                        "error": str(e),
                    })

            # Update import record
            csv_import.accepted_rows = accepted
            csv_import.rejected_rows = rejected
            csv_import.duplicate_rows = duplicates
            csv_import.validation_errors = errors[:100]  # Cap at 100 errors
            csv_import.status = (
                ImportStatus.COMPLETED.value if rejected == 0
                else ImportStatus.PARTIAL.value if accepted > 0
                else ImportStatus.FAILED.value
            )
            csv_import.completed_at = datetime.utcnow()
            csv_import.processing_summary = {
                "total_rows": csv_import.total_rows,
                "accepted": accepted,
                "rejected": rejected,
                "duplicates": duplicates,
                "error_count": len(errors),
            }

            self.db.commit()
            logger.info(
                f"CSV import completed: {filename} - "
                f"accepted={accepted}, rejected={rejected}, duplicates={duplicates}"
            )
            return csv_import

        except Exception as e:
            logger.error(f"CSV import failed: {filename} - {e}")
            csv_import.status = ImportStatus.FAILED.value
            csv_import.validation_errors = [{"error": f"Processing error: {str(e)}"}]
            csv_import.completed_at = datetime.utcnow()
            self.db.commit()
            return csv_import

    def _parse_csv(self, content: bytes) -> pd.DataFrame:
        """Parse CSV content into a DataFrame."""
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")

        df = pd.read_csv(io.StringIO(text))
        # Strip whitespace from column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        return df

    def _map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map various column names to standard names."""
        mapped = pd.DataFrame()
        for standard_name, variants in COLUMN_MAPPINGS.items():
            for variant in variants:
                if variant in df.columns:
                    mapped[standard_name] = df[variant]
                    break
            if standard_name not in mapped.columns:
                mapped[standard_name] = None
        # Carry over any unmapped columns
        for col in df.columns:
            found = False
            for variants in COLUMN_MAPPINGS.values():
                if col in variants:
                    found = True
                    break
            if not found and col not in mapped.columns:
                mapped[col] = df[col]
        return mapped

    def _validate_row(self, row: pd.Series, row_num: int) -> list[dict]:
        """Validate a single row. Returns list of error dicts."""
        errors = []

        # Required: description
        desc = row.get("description")
        if pd.isna(desc) or str(desc).strip() == "":
            errors.append({"row": row_num, "field": "description", "error": "Missing complaint description"})

        # Validate coordinates
        lat = row.get("latitude")
        lon = row.get("longitude")
        if lat is not None and not pd.isna(lat):
            try:
                lat_f = float(lat)
                if lat_f < -90 or lat_f > 90:
                    errors.append({"row": row_num, "field": "latitude", "error": f"Invalid latitude: {lat}"})
            except (ValueError, TypeError):
                errors.append({"row": row_num, "field": "latitude", "error": f"Non-numeric latitude: {lat}"})

        if lon is not None and not pd.isna(lon):
            try:
                lon_f = float(lon)
                if lon_f < -180 or lon_f > 180:
                    errors.append({"row": row_num, "field": "longitude", "error": f"Invalid longitude: {lon}"})
            except (ValueError, TypeError):
                errors.append({"row": row_num, "field": "longitude", "error": f"Non-numeric longitude: {lon}"})

        # Validate date
        date_val = row.get("date")
        if date_val is not None and not pd.isna(date_val):
            try:
                self._parse_date(date_val)
            except Exception:
                errors.append({"row": row_num, "field": "date", "error": f"Invalid date format: {date_val}"})

        return errors

    def _parse_date(self, val) -> datetime:
        """Parse various date formats."""
        if isinstance(val, datetime):
            return val
        val_str = str(val).strip()
        for fmt in [
            "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y %H:%M:%S", "%d-%m-%Y",
            "%m/%d/%Y %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ",
        ]:
            try:
                return datetime.strptime(val_str, fmt)
            except ValueError:
                continue
        return pd.to_datetime(val_str).to_pydatetime()

    def _compute_row_hash(self, row: pd.Series) -> str:
        """Compute a hash for duplicate detection."""
        key_parts = [
            str(row.get("description", "")),
            str(row.get("latitude", "")),
            str(row.get("longitude", "")),
            str(row.get("date", "")),
        ]
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()

    def _is_db_duplicate(self, row: pd.Series) -> bool:
        """Check if a similar complaint already exists in the database."""
        complaint_id = row.get("complaint_id")
        if complaint_id is not None and not pd.isna(complaint_id):
            c_id_str = str(complaint_id).strip()
            if c_id_str and c_id_str.lower() != "nan":
                query = self.db.query(Complaint).filter(Complaint.complaint_id == c_id_str)
                if query.first() is not None:
                    return True

        desc = str(row.get("description", "")).strip()
        lat = row.get("latitude")
        lon = row.get("longitude")

        if not desc:
            return False

        query = self.db.query(Complaint).filter(Complaint.description == desc)

        if lat is not None and not pd.isna(lat) and lon is not None and not pd.isna(lon):
            try:
                query = query.filter(
                    Complaint.latitude == float(lat),
                    Complaint.longitude == float(lon),
                )
            except (ValueError, TypeError):
                pass

        return query.first() is not None

    def _normalize_severity(self, val) -> str:
        """Normalize severity value."""
        if val is None or pd.isna(val):
            return Severity.MEDIUM.value
        val_str = str(val).strip().upper()
        if val_str in VALID_SEVERITIES:
            return val_str
        # Map common values
        mapping = {"1": "LOW", "2": "MEDIUM", "3": "HIGH", "4": "CRITICAL",
                    "MINOR": "LOW", "MAJOR": "HIGH", "URGENT": "CRITICAL"}
        return mapping.get(val_str, Severity.MEDIUM.value)

    def _normalize_category(self, val) -> str:
        """Normalize category/incident_type."""
        if val is None or pd.isna(val):
            return "OTHER"
        val_str = str(val).strip().upper().replace(" ", "_").replace("-", "_")
        if val_str in VALID_CATEGORIES:
            return val_str
        # Fuzzy match
        for cat in VALID_CATEGORIES:
            if cat in val_str or val_str in cat:
                return cat
        return val_str  # Keep original if no match

    def _create_complaint(self, row: pd.Series, import_id: str, data_truth: str) -> Complaint:
        """Create a Complaint object from a CSV row."""
        complaint_id = row.get("complaint_id")
        from app.models.domain import generate_uuid
        if complaint_id is not None and not pd.isna(complaint_id):
            c_id_str = str(complaint_id).strip()
            if c_id_str and c_id_str.lower() != "nan":
                existing = self.db.query(Complaint).filter(Complaint.complaint_id == c_id_str).first()
                if existing:
                    complaint_id = f"{c_id_str}_{import_id[:8]}"
                else:
                    complaint_id = c_id_str
            else:
                complaint_id = generate_uuid()
        else:
            complaint_id = generate_uuid()

        desc = str(row.get("description", "")).strip()
        category = self._normalize_category(row.get("category"))
        severity = self._normalize_severity(row.get("severity"))

        # Parse date
        try:
            reported_at = self._parse_date(row.get("date"))
        except Exception:
            reported_at = datetime.utcnow()

        # Parse coordinates
        lat = None
        lon = None
        try:
            lat_val = row.get("latitude")
            lon_val = row.get("longitude")
            if lat_val is not None and not pd.isna(lat_val):
                lat = float(lat_val)
            if lon_val is not None and not pd.isna(lon_val):
                lon = float(lon_val)
        except (ValueError, TypeError):
            pass

        # Generate title from description
        title = desc[:80] + "..." if len(desc) > 80 else desc

        # Normalize address
        address = None
        original_address = None
        addr_val = row.get("address")
        if addr_val is not None and not pd.isna(addr_val):
            original_address = str(addr_val).strip()
            address = original_address

        # Ward
        ward = None
        ward_val = row.get("ward")
        if ward_val is not None and not pd.isna(ward_val):
            ward = str(ward_val).strip()

        # Assign to site
        site_id = None
        if lat is not None and lon is not None:
            site = self.geo_service.find_or_create_site(lat, lon, ward=ward, address=address)
            site_id = site.site_id

        complaint = Complaint(
            complaint_id=complaint_id,
            import_id=import_id,
            title=title,
            description=desc,
            original_text=desc,
            incident_type=category,
            category=category,
            reported_at=reported_at,
            latitude=lat,
            longitude=lon,
            address=address,
            original_address=original_address,
            ward=ward,
            severity=severity,
            status=ComplaintStatus.NEW.value,
            source="CSV",
            site_id=site_id,
            data_truth=data_truth,
            normalized_at=datetime.utcnow(),
        )
        return complaint

    def get_import_status(self, import_id: str) -> Optional[CSVImport]:
        """Get the status of an import by ID."""
        return self.db.query(CSVImport).filter(CSVImport.import_id == import_id).first()

    def list_imports(self) -> list[CSVImport]:
        """List all imports."""
        return self.db.query(CSVImport).order_by(CSVImport.created_at.desc()).all()
