"""
Pydantic v2 schemas for the Executive Dashboard and Enterprise Health Report.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class KPIMetric(BaseModel):
    label: str
    value: float
    unit: str = ""
    trend: str = "stable"        # up | down | stable
    change_percent: float = 0.0


class DashboardSummary(BaseModel):
    clv_score: KPIMetric
    revenue_forecast: KPIMetric
    employee_performance: KPIMetric
    profit_projection: KPIMetric
    overall_health_score: float = Field(..., ge=0, le=100)
    generated_at: str


class RiskItem(BaseModel):
    area: str
    severity: str       # low | medium | high | critical
    description: str


class Recommendation(BaseModel):
    area: str
    priority: str       # low | medium | high
    action: str


class HealthReport(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    clv_score: float
    revenue_score: float
    employee_score: float
    profit_score: float
    risks: List[RiskItem]
    recommendations: List[Recommendation]
    executive_summary: str
    generated_at: str


class DashboardInput(BaseModel):
    """Inputs for generating dashboard summary — combines sample data for all models."""
    clv_age: int = 35
    clv_gender: str = "Male"
    clv_city: str = "Bangalore"
    clv_total_spent: float = 1500.0
    clv_membership_level: str = "Gold"
    clv_membership_years: int = 3
    clv_number_of_purchases: int = 5

    revenue_units_sold: int = 3
    revenue_region: str = "North"
    revenue_month: int = 6
    revenue_day_of_week: int = 2

    employee_age: int = 35
    employee_years_worked: int = 10
    employee_attendance_percent: float = 92.5
    employee_training_hours: float = 50.0
    employee_promotions: int = 2
    employee_tasks_completed: float = 300.0
    employee_project_success_rate: float = 0.85
    employee_manager_rating: float = 4.2
    employee_peer_rating: float = 4.5
    employee_salary: float = 75000.0

    profit_operational_cost: float = 250000.0
    profit_marketing_cost: float = 50000.0
    profit_revenue: float = 500000.0
