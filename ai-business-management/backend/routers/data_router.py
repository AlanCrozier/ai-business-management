"""
Data API router — seed database, list records, get stats, generate live data.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from database import get_db
from models.dataset_models import (
    CustomerRecord,
    EmployeeRecord,
    SalesRecord,
    FinanceRecord,
)
from services.data_generator import DataGeneratorService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/data", tags=["Data Generation"])

generator = DataGeneratorService()

# ── Pydantic Schemas for single inserts ──────────────────────────────────────
class SalesCreate(BaseModel):
    product_id: str
    region: str
    units_sold: int
    revenue: float

class CustomerCreate(BaseModel):
    customer_id: str
    age: int
    city: str
    membership_level: str
    lifetime_value: float

class EmployeeCreate(BaseModel):
    employee_id: str
    role: str
    years_worked: int
    attendance_percent: float
    performance_score: float


# ── Helper: bulk insert dicts → ORM objects ──────────────────────────────────
def _bulk_insert(db: Session, model_class, records: list[dict]) -> int:
    """Insert a list of dicts as ORM objects. Returns count inserted."""
    objects = [model_class(**r) for r in records]
    db.bulk_save_objects(objects)
    db.commit()
    return len(objects)


# ── Seed all tables ──────────────────────────────────────────────────────────
@router.post("/seed")
def seed_database(
    customers: int = Query(500, ge=1, le=10_000, description="Number of customer records"),
    employees: int = Query(500, ge=1, le=10_000, description="Number of employee records"),
    sales: int = Query(500, ge=1, le=10_000, description="Number of sales records"),
    finance: int = Query(500, ge=1, le=5_000, description="Number of finance records"),
    db: Session = Depends(get_db),
):
    """Seed all 4 dataset tables with realistic generated data."""
    results = {}

    cust_data = generator.generate_customers(customers)
    results["customers"] = _bulk_insert(db, CustomerRecord, cust_data)

    emp_data = generator.generate_employees(employees)
    results["employees"] = _bulk_insert(db, EmployeeRecord, emp_data)

    sales_data = generator.generate_sales(sales)
    results["sales"] = _bulk_insert(db, SalesRecord, sales_data)

    fin_data = generator.generate_finance(finance)
    results["finance_records"] = _bulk_insert(db, FinanceRecord, fin_data)

    logger.info("Database seeded: %s", results)
    return {"status": "seeded", "records_inserted": results}


# ── Generate live (real-time) data ───────────────────────────────────────────
@router.post("/generate-live")
def generate_live(
    customers: int = Query(5, ge=1, le=100),
    employees: int = Query(5, ge=1, le=100),
    sales: int = Query(10, ge=1, le=200),
    finance: int = Query(3, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Generate a small batch of 'live' records timestamped now."""
    batch = generator.generate_live_batch(customers, employees, sales, finance)
    results = {
        "customers": _bulk_insert(db, CustomerRecord, batch["customers"]),
        "employees": _bulk_insert(db, EmployeeRecord, batch["employees"]),
        "sales": _bulk_insert(db, SalesRecord, batch["sales"]),
        "finance_records": _bulk_insert(db, FinanceRecord, batch["finance"]),
    }
    logger.info("Live data generated: %s", results)
    return {"status": "live_generated", "records_inserted": results}


# ── Stats ────────────────────────────────────────────────────────────────────
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Return row counts and latest record timestamps for all tables."""
    def _table_stats(model):
        count = db.query(func.count(model.id)).scalar() or 0
        latest = db.query(func.max(model.created_at)).scalar()
        return {
            "count": count,
            "latest_record": latest.isoformat() if latest else None,
        }

    return {
        "customers": _table_stats(CustomerRecord),
        "employees": _table_stats(EmployeeRecord),
        "sales": _table_stats(SalesRecord),
        "finance_records": _table_stats(FinanceRecord),
    }


# ── List endpoints with pagination ──────────────────────────────────────────
def _serialize(obj) -> dict:
    """Convert an ORM object to a dict, handling date/datetime fields."""
    d = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if hasattr(val, "isoformat"):
            val = val.isoformat()
        d[col.name] = val
    return d


@router.get("/customers")
def list_customers(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List customer records with pagination."""
    rows = (
        db.query(CustomerRecord)
        .order_by(CustomerRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {"total": db.query(func.count(CustomerRecord.id)).scalar(), "data": [_serialize(r) for r in rows]}


@router.get("/employees")
def list_employees(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List employee records with pagination."""
    rows = (
        db.query(EmployeeRecord)
        .order_by(EmployeeRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {"total": db.query(func.count(EmployeeRecord.id)).scalar(), "data": [_serialize(r) for r in rows]}


@router.get("/sales")
def list_sales(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List sales records with pagination."""
    rows = (
        db.query(SalesRecord)
        .order_by(SalesRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {"total": db.query(func.count(SalesRecord.id)).scalar(), "data": [_serialize(r) for r in rows]}

@router.post("/sales")
def create_sale(sale: SalesCreate, db: Session = Depends(get_db)):
    """Record a new sale."""
    import datetime
    from datetime import timezone
    new_record = SalesRecord(
        order_id=f"ORD-{int(datetime.datetime.now().timestamp())}",
        date=datetime.date.today(),
        customer_id="CUST-MANUAL",
        product_id=sale.product_id,
        region=sale.region,
        units_sold=sale.units_sold,
        revenue=sale.revenue,
        month=datetime.date.today().month,
        day_of_week=datetime.date.today().weekday()
    )
    db.add(new_record)
    db.commit()
    return {"success": True, "record": _serialize(new_record)}

@router.post("/customers")
def create_customer(cust: CustomerCreate, db: Session = Depends(get_db)):
    """Record a new customer."""
    new_record = CustomerRecord(
        customer_id=cust.customer_id,
        age=cust.age,
        gender="Unknown",
        city=cust.city,
        total_spent=cust.lifetime_value,
        membership_level=cust.membership_level,
        membership_years=1,
        number_of_purchases=1,
        lifetime_value=cust.lifetime_value
    )
    db.add(new_record)
    db.commit()
    return {"success": True, "record": _serialize(new_record)}

@router.post("/employees")
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    """Record a new employee."""
    new_record = EmployeeRecord(
        employee_id=emp.employee_id,
        age=30,
        department="General",
        job_level=emp.role,
        work_mode="Office",
        years_worked=emp.years_worked,
        attendance_percent=emp.attendance_percent,
        training_hours=0,
        promotions=0,
        tasks_completed=0,
        project_success_rate=0,
        manager_rating=0,
        peer_rating=0,
        salary=0,
        performance_score=emp.performance_score
    )
    db.add(new_record)
    db.commit()
    return {"success": True, "record": _serialize(new_record)}


@router.get("/finance")
def list_finance(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List finance records with pagination."""
    rows = (
        db.query(FinanceRecord)
        .order_by(FinanceRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {"total": db.query(func.count(FinanceRecord.id)).scalar(), "data": [_serialize(r) for r in rows]}
