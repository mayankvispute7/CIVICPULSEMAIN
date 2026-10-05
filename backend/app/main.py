"""
Main FastAPI application entrypoint.
"""
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.api.routers import ingestion, complaints, analysis, execution, outcomes
import app.models.domain
from app.schemas.api_schemas import HealthResponse

# Create database tables
# In production, use Alembic migrations instead of create_all
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Civic Pulse API - Infrastructure failure intelligence platform",
    version="1.0.0",
)

# Set all CORS enabled origins
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "database": "sqlite" if settings.USE_SQLITE else "postgres",
        "timestamp": datetime.utcnow(),
    }

# Include routers (mount under /api/v1 and root for frontend compatibility)
for pfx in [settings.API_V1_STR, ""]:
    app.include_router(ingestion.router, prefix=pfx)
    app.include_router(complaints.router, prefix=pfx)
    app.include_router(analysis.router, prefix=pfx)
    app.include_router(execution.router, prefix=pfx)
    app.include_router(outcomes.router, prefix=pfx)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
