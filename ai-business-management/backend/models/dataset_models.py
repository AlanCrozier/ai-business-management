"""
SQLAlchemy ORM models for the 4 core business datasets.
These tables store the generated (and potentially imported) raw data
that feeds the ML prediction pipeline and the executive dashboard.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from datetime import datetime, timezone

from database import Base


# ── Customer Dataset ─────────────────────────────────────────────────────────
class CustomerRecord(Base):
    """Raw customer data — mirrors the CLV training CSV."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(String(20), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)              # Male / Female
    city = Column(String(30), nullable=False)                # Bangalore / Delhi / Mumbai
    total_spent = Column(Float, nullable=False)
    membership_level = Column(String(15), nullable=False)    # Silver / Gold / Platinum
    membership_years = Column(Integer, nullable=False)
    number_of_purchases = Column(Integer, nullable=False)
    lifetime_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── Employee Dataset ─────────────────────────────────────────────────────────
class EmployeeRecord(Base):
    """Raw employee data — mirrors the Employee Performance training CSV."""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String(20), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    department = Column(String(30), nullable=False)          # Engineering / Sales / HR / …
    job_level = Column(String(15), nullable=False)           # Junior / Mid / Senior / Lead
    work_mode = Column(String(15), nullable=False)           # Office / Remote / Hybrid
    years_worked = Column(Integer, nullable=False)
    attendance_percent = Column(Float, nullable=False)
    training_hours = Column(Float, nullable=False)
    promotions = Column(Integer, nullable=False)
    tasks_completed = Column(Float, nullable=False)
    project_success_rate = Column(Float, nullable=False)
    manager_rating = Column(Float, nullable=False)
    peer_rating = Column(Float, nullable=False)
    salary = Column(Float, nullable=False)
    performance_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── Sales / Revenue Dataset ──────────────────────────────────────────────────
class SalesRecord(Base):
    """Raw sales data — mirrors the Revenue / Sales training CSV."""
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False)
    customer_id = Column(String(20), nullable=False)
    product_id = Column(String(20), nullable=False)
    region = Column(String(10), nullable=False)              # North / South / East / West
    units_sold = Column(Integer, nullable=False)
    revenue = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── Finance / Profit Dataset ─────────────────────────────────────────────────
class FinanceRecord(Base):
    """Raw finance data — mirrors the Profit training CSV."""
    __tablename__ = "finance_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, nullable=False, index=True)
    month = Column(String(10), nullable=False)               # e.g. "2026-03"
    operational_cost = Column(Float, nullable=False)
    marketing_cost = Column(Float, nullable=False)
    revenue = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
