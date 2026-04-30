"""
Prediction API router — individual model prediction endpoints + history.
"""
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.prediction import PredictionRecord
from services.ml_service import MLService
from schemas.clv import CLVInput, CLVOutput
from schemas.revenue import RevenueInput, RevenueOutput
from schemas.employee import EmployeeInput, EmployeeOutput
from schemas.profit import ProfitInput, ProfitOutput

router = APIRouter(prefix="/api/predict", tags=["Predictions"])

ml = MLService.get_instance()


# ── CLV ──────────────────────────────────────────────────────────────────────
@router.post("/clv", response_model=CLVOutput)
def predict_clv(data: CLVInput, db: Session = Depends(get_db)):
    """Predict Customer Lifetime Value."""
    try:
        value = ml.predict_clv(
            age=data.age,
            gender=data.gender,
            city=data.city,
            total_spent=data.total_spent,
            membership_level=data.membership_level,
            membership_years=data.membership_years,
            number_of_purchases=data.number_of_purchases,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    confidence = "High" if value > 2000 else "Medium" if value > 1000 else "Low"

    # Persist
    record = PredictionRecord(
        model_type="clv",
        input_data=data.model_dump_json(),
        result=json.dumps({"predicted_lifetime_value": value}),
        predicted_value=value,
    )
    db.add(record)
    db.commit()

    return CLVOutput(
        predicted_lifetime_value=round(value, 2),
        confidence_label=confidence,
        input_summary=data.model_dump(),
    )


# ── Revenue ──────────────────────────────────────────────────────────────────
@router.post("/revenue", response_model=RevenueOutput)
def predict_revenue(data: RevenueInput, db: Session = Depends(get_db)):
    """Predict revenue for a sale."""
    try:
        value = ml.predict_revenue(
            units_sold=data.units_sold,
            region=data.region,
            month=data.month,
            day_of_week=data.day_of_week,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    confidence = "High" if value > 300 else "Medium" if value > 100 else "Low"

    record = PredictionRecord(
        model_type="revenue",
        input_data=data.model_dump_json(),
        result=json.dumps({"predicted_revenue": value}),
        predicted_value=value,
    )
    db.add(record)
    db.commit()

    return RevenueOutput(
        predicted_revenue=round(value, 2),
        confidence_label=confidence,
        input_summary=data.model_dump(),
    )


# ── Employee ─────────────────────────────────────────────────────────────────
@router.post("/employee", response_model=EmployeeOutput)
def predict_employee(data: EmployeeInput, db: Session = Depends(get_db)):
    """Predict employee performance score."""
    try:
        value = ml.predict_employee(
            age=data.age,
            years_worked=data.years_worked,
            attendance_percent=data.attendance_percent,
            training_hours=data.training_hours,
            promotions=data.promotions,
            tasks_completed=data.tasks_completed,
            project_success_rate=data.project_success_rate,
            manager_rating=data.manager_rating,
            peer_rating=data.peer_rating,
            salary=data.salary,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if value >= 4.0:
        tier = "Outstanding"
    elif value >= 3.0:
        tier = "High"
    elif value >= 2.0:
        tier = "Average"
    else:
        tier = "Low"

    record = PredictionRecord(
        model_type="employee",
        input_data=data.model_dump_json(),
        result=json.dumps({"predicted_performance_score": value}),
        predicted_value=value,
    )
    db.add(record)
    db.commit()

    return EmployeeOutput(
        predicted_performance_score=round(value, 2),
        performance_tier=tier,
        input_summary=data.model_dump(),
    )


# ── Profit ───────────────────────────────────────────────────────────────────
@router.post("/profit", response_model=ProfitOutput)
def predict_profit(data: ProfitInput, db: Session = Depends(get_db)):
    """Predict net profit."""
    try:
        value = ml.predict_profit(
            operational_cost=data.operational_cost,
            marketing_cost=data.marketing_cost,
            revenue=data.revenue,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    margin = (value / data.revenue * 100) if data.revenue > 0 else 0
    confidence = "High" if margin > 20 else "Medium" if margin > 5 else "Low"

    record = PredictionRecord(
        model_type="profit",
        input_data=data.model_dump_json(),
        result=json.dumps({"predicted_profit": value}),
        predicted_value=value,
    )
    db.add(record)
    db.commit()

    return ProfitOutput(
        predicted_profit=round(value, 2),
        profit_margin_percent=round(margin, 2),
        confidence_label=confidence,
        input_summary=data.model_dump(),
    )


# ── History ──────────────────────────────────────────────────────────────────
@router.get("/history")
def get_history(
    model_type: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Retrieve prediction history, optionally filtered by model type."""
    query = db.query(PredictionRecord).order_by(PredictionRecord.created_at.desc())
    if model_type:
        query = query.filter(PredictionRecord.model_type == model_type)
    records = query.limit(limit).all()
    return [
        {
            "id": r.id,
            "model_type": r.model_type,
            "input_data": json.loads(r.input_data),
            "result": json.loads(r.result),
            "predicted_value": r.predicted_value,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
