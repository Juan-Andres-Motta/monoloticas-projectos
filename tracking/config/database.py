import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL - using PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://tracking_user:tracking_password@localhost:5432/trackingdb",
)

# Create engine with PostgreSQL optimizations
engine = create_engine(
    DATABASE_URL, pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=300
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
