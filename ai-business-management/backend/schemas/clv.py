"""
Pydantic v2 schemas for Customer Lifetime Value predictions.
Model features: age, gender, city, total_spent, membership_level, membership_years, number_of_purchases
Target: lifetime_value
"""
from pydantic import BaseModel, Field
from typing import Optional


class CLVInput(BaseModel):
    age: int = Field(..., ge=18, le=100, description="Customer age")
    gender: str = Field(..., description="Male or Female")
    city: str = Field(..., description="City name (Bangalore, Delhi, Mumbai)")
    total_spent: float = Field(..., ge=0, description="Total amount spent by customer")
    membership_level: str = Field(..., description="Silver, Gold, or Platinum")
    membership_years: int = Field(..., ge=0, le=30, description="Years as a member")
    number_of_purchases: int = Field(..., ge=0, description="Total number of purchases")

    model_config = {"json_schema_extra": {
        "examples": [{
            "age": 35, "gender": "Male", "city": "Bangalore",
            "total_spent": 1500.0, "membership_level": "Gold",
            "membership_years": 3, "number_of_purchases": 5,
        }]
    }}


class CLVOutput(BaseModel):
    predicted_lifetime_value: float
    confidence_label: str  # Low / Medium / High
    input_summary: Optional[dict] = None
