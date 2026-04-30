"""
Pydantic v2 schemas for Revenue / Sales predictions.
Model features: units_sold, region (encoded), month, day_of_week
Target: revenue
"""
from pydantic import BaseModel, Field
from typing import Optional


class RevenueInput(BaseModel):
    units_sold: int = Field(..., ge=1, description="Number of units sold")
    region: str = Field(..., description="Region (North, South, East, West)")
    month: int = Field(..., ge=1, le=12, description="Month of sale (1-12)")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Mon … 6=Sun)")

    model_config = {"json_schema_extra": {
        "examples": [{
            "units_sold": 3, "region": "North", "month": 6, "day_of_week": 2,
        }]
    }}


class RevenueOutput(BaseModel):
    predicted_revenue: float
    confidence_label: str
    input_summary: Optional[dict] = None
