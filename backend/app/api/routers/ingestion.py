"""Router for ingestion endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.services.csv_ingestion_service import CSVIngestionService
from app.schemas.api_schemas import ImportSummary
from app.models.enums import DataTruth

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@router.post("/csv", response_model=ImportSummary)
async def upload_csv(
    file: UploadFile = File(...),
    data_truth: str = Form(DataTruth.REAL_DATA.value),
    db: Session = Depends(get_db)
):
    """Upload and process a CSV file of complaints."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    service = CSVIngestionService(db)
    
    # Run ingestion (synchronously for MVP/hackathon)
    csv_import = service.ingest_csv(file.filename, content, data_truth)
    
    return csv_import

@router.get("/imports", response_model=list[ImportSummary])
def list_imports(db: Session = Depends(get_db)):
    """List all CSV imports."""
    service = CSVIngestionService(db)
    return service.list_imports()

@router.get("/imports/{import_id}", response_model=ImportSummary)
def get_import(import_id: str, db: Session = Depends(get_db)):
    """Get the status of a specific import."""
    service = CSVIngestionService(db)
    imp = service.get_import_status(import_id)
    if not imp:
        raise HTTPException(status_code=404, detail="Import not found")
    return imp
