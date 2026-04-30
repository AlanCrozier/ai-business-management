"""
Pydantic v2 schemas for Employee performance predictions.
Model features: age, years_worked, attendance_percent, training_hours, promotions,
                tasks_completed, project_success_rate, manager_rating, peer_rating, salary
Target: performance_score
"""
from pydantic import BaseModel, Field
from typing import Optional


class EmployeeInput(BaseModel):
    age: int = Field(..., ge=18, le=70, description="Employee age")
    years_worked: int = Field(..., ge=0, le=50, description="Years at the company")
    attendance_percent: float = Field(..., ge=0, le=100, description="Attendance %")
    training_hours: float = Field(..., ge=0, description="Training hours completed")
    promotions: int = Field(..., ge=0, description="Number of promotions")
    tasks_completed: float = Field(..., ge=0, description="Tasks completed count")
    project_success_rate: float = Field(..., ge=0, le=1, description="Project success rate (0-1)")
    manager_rating: float = Field(..., ge=0, le=5, description="Manager rating (0-5)")
    peer_rating: float = Field(..., ge=0, le=5, description="Peer rating (0-5)")
    salary: float = Field(..., ge=0, description="Current salary")

    model_config = {"json_schema_extra": {
        "examples": [{
            "age": 35, "years_worked": 10, "attendance_percent": 92.5,
            "training_hours": 50, "promotions": 2, "tasks_completed": 300,
            "project_success_rate": 0.85, "manager_rating": 4.2,
            "peer_rating": 4.5, "salary": 75000,
        }]
    }}


class EmployeeOutput(BaseModel):
    predicted_performance_score: float
    performance_tier: str  # Low / Average / High / Outstanding
    input_summary: Optional[dict] = None
