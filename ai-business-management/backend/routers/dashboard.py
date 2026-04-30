"""
Dashboard & Enterprise Health Report router.
Combines outputs from all 4 models into cohesive business metrics.
"""
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services.ml_service import MLService
from schemas.dashboard import (
    DashboardInput,
    DashboardSummary,
    HealthReport,
    KPIMetric,
    RiskItem,
    Recommendation,
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

ml = MLService.get_instance()


def _score_to_100(value: float, min_v: float, max_v: float) -> float:
    """Normalise a value to a 0-100 scale."""
    if max_v == min_v:
        return 50.0
    return max(0, min(100, (value - min_v) / (max_v - min_v) * 100))


@router.post("/summary", response_model=DashboardSummary)
def get_dashboard_summary(data: DashboardInput):
    """Run all 4 models and return a combined KPI dashboard."""
    try:
        clv_val = ml.predict_clv(
            data.clv_age, data.clv_gender, data.clv_city,
            data.clv_total_spent, data.clv_membership_level,
            data.clv_membership_years, data.clv_number_of_purchases,
        )
    except Exception:
        clv_val = 0

    try:
        rev_val = ml.predict_revenue(
            data.revenue_units_sold, data.revenue_region,
            data.revenue_month, data.revenue_day_of_week,
        )
    except Exception:
        rev_val = 0

    try:
        emp_val = ml.predict_employee(
            data.employee_age, data.employee_years_worked,
            data.employee_attendance_percent, data.employee_training_hours,
            data.employee_promotions, data.employee_tasks_completed,
            data.employee_project_success_rate, data.employee_manager_rating,
            data.employee_peer_rating, data.employee_salary,
        )
    except Exception:
        emp_val = 0

    try:
        profit_val = ml.predict_profit(
            data.profit_operational_cost, data.profit_marketing_cost,
            data.profit_revenue,
        )
    except Exception:
        profit_val = 0

    # Normalise scores to 0-100
    clv_score = _score_to_100(clv_val, 0, 5000)
    rev_score = _score_to_100(rev_val, 0, 1000)
    emp_score = _score_to_100(emp_val, 1, 5)
    profit_margin = (profit_val / data.profit_revenue * 100) if data.profit_revenue > 0 else 0
    profit_score = _score_to_100(profit_margin, -50, 50)

    overall = (clv_score + rev_score + emp_score + profit_score) / 4

    return DashboardSummary(
        clv_score=KPIMetric(
            label="Customer Lifetime Value",
            value=round(clv_val, 2),
            unit="$",
            trend="up" if clv_val > 1500 else "down",
            change_percent=round(clv_score, 1),
        ),
        revenue_forecast=KPIMetric(
            label="Revenue Forecast",
            value=round(rev_val, 2),
            unit="$",
            trend="up" if rev_val > 200 else "stable",
            change_percent=round(rev_score, 1),
        ),
        employee_performance=KPIMetric(
            label="Employee Performance",
            value=round(emp_val, 2),
            unit="/5",
            trend="up" if emp_val > 3.5 else "stable",
            change_percent=round(emp_score, 1),
        ),
        profit_projection=KPIMetric(
            label="Profit Projection",
            value=round(profit_val, 2),
            unit="$",
            trend="up" if profit_margin > 15 else "down",
            change_percent=round(profit_score, 1),
        ),
        overall_health_score=round(overall, 1),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/health-report", response_model=HealthReport)
def get_health_report(data: DashboardInput):
    """Generate a comprehensive Enterprise Health Report."""
    try:
        clv_val = ml.predict_clv(
            data.clv_age, data.clv_gender, data.clv_city,
            data.clv_total_spent, data.clv_membership_level,
            data.clv_membership_years, data.clv_number_of_purchases,
        )
    except Exception:
        clv_val = 0

    try:
        rev_val = ml.predict_revenue(
            data.revenue_units_sold, data.revenue_region,
            data.revenue_month, data.revenue_day_of_week,
        )
    except Exception:
        rev_val = 0

    try:
        emp_val = ml.predict_employee(
            data.employee_age, data.employee_years_worked,
            data.employee_attendance_percent, data.employee_training_hours,
            data.employee_promotions, data.employee_tasks_completed,
            data.employee_project_success_rate, data.employee_manager_rating,
            data.employee_peer_rating, data.employee_salary,
        )
    except Exception:
        emp_val = 0

    try:
        profit_val = ml.predict_profit(
            data.profit_operational_cost, data.profit_marketing_cost,
            data.profit_revenue,
        )
    except Exception:
        profit_val = 0

    # Score each domain 0-100
    clv_s = _score_to_100(clv_val, 0, 5000)
    rev_s = _score_to_100(rev_val, 0, 1000)
    emp_s = _score_to_100(emp_val, 1, 5)
    profit_margin = (profit_val / data.profit_revenue * 100) if data.profit_revenue > 0 else 0
    profit_s = _score_to_100(profit_margin, -50, 50)
    overall = (clv_s + rev_s + emp_s + profit_s) / 4

    # Build risks
    risks: list[RiskItem] = []
    if clv_s < 40:
        risks.append(RiskItem(area="Customer Value", severity="high",
                              description="CLV is below target. Consider retention campaigns."))
    if rev_s < 40:
        risks.append(RiskItem(area="Revenue", severity="high",
                              description="Revenue forecast is low. Review pricing & sales strategy."))
    if emp_s < 40:
        risks.append(RiskItem(area="Workforce", severity="medium",
                              description="Employee performance needs improvement. Invest in training."))
    if profit_s < 40:
        risks.append(RiskItem(area="Profitability", severity="critical",
                              description="Profit margins are thin. Audit operational costs."))
    if not risks:
        risks.append(RiskItem(area="General", severity="low",
                              description="All metrics are within healthy ranges."))

    # Build recommendations
    recs: list[Recommendation] = []
    if clv_s < 60:
        recs.append(Recommendation(area="Customer", priority="high",
                                   action="Launch loyalty programmes to increase customer lifetime value."))
    if rev_s < 60:
        recs.append(Recommendation(area="Sales", priority="high",
                                   action="Expand into new regions and optimise product mix."))
    if emp_s < 60:
        recs.append(Recommendation(area="HR", priority="medium",
                                   action="Increase training hours and revise promotion criteria."))
    if profit_s < 60:
        recs.append(Recommendation(area="Finance", priority="high",
                                   action="Reduce operational costs and renegotiate vendor contracts."))
    if not recs:
        recs.append(Recommendation(area="Strategy", priority="low",
                                   action="Maintain current trajectory. Consider scaling operations."))

    summary_parts = [
        f"Enterprise health score: {overall:.0f}/100.",
        f"CLV: ${clv_val:,.0f} (score {clv_s:.0f}).",
        f"Revenue forecast: ${rev_val:,.0f} (score {rev_s:.0f}).",
        f"Employee performance: {emp_val:.2f}/5 (score {emp_s:.0f}).",
        f"Profit projection: ${profit_val:,.0f} with {profit_margin:.1f}% margin (score {profit_s:.0f}).",
    ]

    return HealthReport(
        overall_score=round(overall, 1),
        clv_score=round(clv_s, 1),
        revenue_score=round(rev_s, 1),
        employee_score=round(emp_s, 1),
        profit_score=round(profit_s, 1),
        risks=risks,
        recommendations=recs,
        executive_summary=" ".join(summary_parts),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
