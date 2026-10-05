"""Database connection and session management."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


def _get_engine():
    """Create database engine based on configuration."""
    db_url = settings.db_url
    connect_args = {}

    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        db_url,
        echo=settings.DEBUG,
        connect_args=connect_args,
        pool_pre_ping=True if not db_url.startswith("sqlite") else False,
    )

    # Enable WAL mode and foreign keys for SQLite
    if db_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency: yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Use for development/demo only."""
    Base.metadata.create_all(bind=engine)


def reset_db():
    """Drop and recreate all tables. Use for testing only."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
