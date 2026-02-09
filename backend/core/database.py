"""Database configuration and session management.

Uses SQLAlchemy 2.0 ORM with SQLite for local development.
Portable types allow seamless migration to PostgreSQL.
"""

from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool

# Environment-based URL for migration-ready setup
# Default to a deterministic DB file inside the backend package so scripts
# and the running server use the same file regardless of current working dir.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
default_sqlite_path = os.path.join(base_dir, "health_smc.db")
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{default_sqlite_path}"
)

# SQLite-specific: check_same_thread=False allows async access
# This is safe for single-threaded FastAPI with lifespan management
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=False,  # Set to True for SQL debug logging
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session.

    Yields:
        SQLAlchemy Session instance for HTTP request lifetime.

    Example:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables based on models.

    Called once at application startup.
    Safe to call multiple times (idempotent).
    """
    Base.metadata.create_all(bind=engine)
