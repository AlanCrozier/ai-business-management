"""
Pydantic v2 schemas for Profit predictions.
Model features: operational_cost, marketing_cost, revenue
Target: profit
"""
from pydantic import BaseModel, Field
from typing import Optional


class ProfitInput(BaseModel):
    operational_cost: float = Field(..., ge=0, description="Operational cost ($)")
    marketing_cost: float = Field(..., ge=0, description="Marketing cost ($)")
    revenue: float = Field(..., ge=0, description="Revenue ($)")

    model_config = {"json_schema_extra": {
        "examples": [{
            "operational_cost": 250000, "marketing_cost": 50000, "revenue": 500000,
        }]
    }}


class ProfitOutput(BaseModel):
    predicted_profit: float
    profit_margin_percent: float
    confidence_label: str
    input_summary: Optional[dict] = None
