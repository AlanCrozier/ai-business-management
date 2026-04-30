"""
Database configuration — SQLAlchemy + MySQL for all application data.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read from Render environment variable, fallback to local MySQL
raw_db_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:%23Alan123@localhost:3306/Lumon")
# SQLAlchemy 1.4+ requires postgresql:// instead of postgres://
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = raw_db_url


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,       # auto-reconnect on stale connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import models so Base.metadata knows about all tables
# (must come AFTER Base is defined to avoid circular imports)
import models.prediction          # noqa: E402, F401
import models.dataset_models      # noqa: E402, F401
import models.user_account        # noqa: E402, F401
