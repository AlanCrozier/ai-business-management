"""
SQLAlchemy ORM model for storing prediction history.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime, timezone

from database import Base


class PredictionRecord(Base):
    """Stores every prediction made through the API."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_type = Column(String(20), nullable=False, index=True)  # clv | revenue | employee | profit
    input_data = Column(Text, nullable=False)   # JSON-serialised input
    result = Column(Text, nullable=False)        # JSON-serialised output
    predicted_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
