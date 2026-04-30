"""
Data Generator Service — produces realistic, correlated business data
for all 4 ML model domains.

Each generator returns a list of dicts ready for ORM bulk-insert.
Uses Python's `random` module with carefully-tuned distributions so the
generated data mirrors the patterns found in the original training CSVs.
"""
from __future__ import annotations

import random
import logging
from datetime import datetime, date, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
GENDERS = ["Male", "Female"]
CITIES = ["Bangalore", "Delhi", "Mumbai"]
MEMBERSHIP_LEVELS = ["Silver", "Gold", "Platinum"]
REGIONS = ["North", "South", "East", "West"]
DEPARTMENTS = ["Engineering", "Sales", "HR", "Marketing", "Finance", "Operations"]
JOB_LEVELS = ["Junior", "Mid", "Senior", "Lead"]
WORK_MODES = ["Office", "Remote", "Hybrid"]

# Salary ranges by job level (annual, INR-style but works for any currency)
SALARY_RANGES: dict[str, tuple[float, float]] = {
    "Junior": (30_000, 55_000),
    "Mid": (50_000, 85_000),
    "Senior": (75_000, 120_000),
    "Lead": (100_000, 160_000),
}

# Spending multipliers by membership level
SPEND_MULTIPLIER: dict[str, float] = {
    "Silver": 1.0,
    "Gold": 1.8,
    "Platinum": 3.0,
}

# Base price per unit (varies ±30 %)
BASE_UNIT_PRICE = 55.0

# Seasonal revenue factor (1-indexed months)
SEASONAL_FACTOR = {
    1: 0.85, 2: 0.80, 3: 0.90, 4: 0.95, 5: 1.00, 6: 1.05,
    7: 1.00, 8: 0.95, 9: 1.05, 10: 1.15, 11: 1.25, 12: 1.35,
}


def _random_date_in_last_n_months(n: int = 12) -> datetime:
    """Return a random datetime within the last *n* months."""
    today = datetime.now(timezone.utc)
    days_back = random.randint(0, n * 30)
    return today - timedelta(days=days_back)


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


# ═════════════════════════════════════════════════════════════════════════════
class DataGeneratorService:
    """Stateless service — call generate_*(count) to get lists of dicts."""

    # ── Customers ────────────────────────────────────────────────────────
    @staticmethod
    def generate_customers(count: int = 500) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for i in range(count):
            age = int(_clamp(random.gauss(38, 12), 18, 75))
            gender = random.choice(GENDERS)
            city = random.choice(CITIES)
            membership = random.choices(
                MEMBERSHIP_LEVELS, weights=[50, 35, 15], k=1
            )[0]

            # Years correlated with age (can't be a member longer than adult life)
            max_years = max(0, age - 18)
            membership_years = random.randint(0, min(max_years, 20))

            # Purchases grow with membership years
            base_purchases = random.randint(1, 15)
            number_of_purchases = base_purchases + membership_years * random.randint(0, 3)

            # Spend correlated with membership + purchases
            multiplier = SPEND_MULTIPLIER[membership]
            total_spent = round(
                random.gauss(500, 200) * multiplier
                + number_of_purchases * random.uniform(20, 80),
                2,
            )
            total_spent = max(50, total_spent)

            # Lifetime value (rough: spend × years × loyalty factor)
            lifetime_value = round(
                total_spent * (1 + membership_years * 0.15)
                + random.gauss(0, 200),
                2,
            )
            lifetime_value = max(100, lifetime_value)

            records.append({
                "customer_id": f"C{10000 + i}",
                "age": age,
                "gender": gender,
                "city": city,
                "total_spent": total_spent,
                "membership_level": membership,
                "membership_years": membership_years,
                "number_of_purchases": number_of_purchases,
                "lifetime_value": lifetime_value,
                "created_at": _random_date_in_last_n_months(12),
            })
        logger.info("Generated %d customer records", count)
        return records

    # ── Employees ────────────────────────────────────────────────────────
    @staticmethod
    def generate_employees(count: int = 500) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for i in range(count):
            age = int(_clamp(random.gauss(35, 10), 21, 65))
            department = random.choice(DEPARTMENTS)
            job_level = random.choices(
                JOB_LEVELS, weights=[35, 30, 25, 10], k=1
            )[0]
            work_mode = random.choice(WORK_MODES)

            max_exp = max(0, age - 22)
            years_worked = random.randint(0, min(max_exp, 35))

            attendance = round(_clamp(random.gauss(88, 8), 50, 100), 1)
            training_hours = round(max(0, random.gauss(45, 20)), 1)

            # Promotions loosely tied to years
            promotions = min(years_worked // 3, random.randint(0, 5))

            tasks_completed = round(max(10, random.gauss(250, 100) + years_worked * 10), 1)
            project_success_rate = round(
                _clamp(random.gauss(0.75, 0.12), 0.2, 1.0), 2
            )

            # Ratings slightly correlated with success + training
            base_rating = 2.5 + project_success_rate * 1.5 + training_hours / 200
            manager_rating = round(
                _clamp(base_rating + random.gauss(0, 0.4), 1.0, 5.0), 1
            )
            peer_rating = round(
                _clamp(base_rating + random.gauss(0, 0.3), 1.0, 5.0), 1
            )

            lo, hi = SALARY_RANGES[job_level]
            salary = round(random.uniform(lo, hi) + years_worked * 800, 2)

            # Performance score: composite of other metrics
            perf = (
                attendance / 100 * 1.0
                + project_success_rate * 1.5
                + (manager_rating + peer_rating) / 10 * 1.5
                + training_hours / 100 * 0.5
                + random.gauss(0, 0.15)
            )
            performance_score = round(_clamp(perf, 1.0, 5.0), 2)

            records.append({
                "employee_id": f"E{10000 + i}",
                "age": age,
                "department": department,
                "job_level": job_level,
                "work_mode": work_mode,
                "years_worked": years_worked,
                "attendance_percent": attendance,
                "training_hours": training_hours,
                "promotions": promotions,
                "tasks_completed": tasks_completed,
                "project_success_rate": project_success_rate,
                "manager_rating": manager_rating,
                "peer_rating": peer_rating,
                "salary": salary,
                "performance_score": performance_score,
                "created_at": _random_date_in_last_n_months(12),
            })
        logger.info("Generated %d employee records", count)
        return records

    # ── Sales / Revenue ──────────────────────────────────────────────────
    @staticmethod
    def generate_sales(count: int = 500) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for i in range(count):
            sale_date = _random_date_in_last_n_months(12)
            region = random.choice(REGIONS)
            units = random.randint(1, 10)
            month_num = sale_date.month
            dow = sale_date.weekday()  # 0=Mon … 6=Sun

            # Revenue = units × base_price × seasonal × regional noise
            season = SEASONAL_FACTOR.get(month_num, 1.0)
            price_per_unit = BASE_UNIT_PRICE * random.uniform(0.7, 1.3)
            revenue = round(units * price_per_unit * season, 2)

            records.append({
                "order_id": f"ORD{90000 + i}",
                "date": sale_date.date(),
                "customer_id": f"C{random.randint(10000, 19999)}",
                "product_id": f"P{random.randint(100, 999)}",
                "region": region,
                "units_sold": units,
                "revenue": revenue,
                "month": month_num,
                "day_of_week": dow,
                "created_at": sale_date,
            })
        logger.info("Generated %d sales records", count)
        return records

    # ── Finance / Profit ─────────────────────────────────────────────────
    @staticmethod
    def generate_finance(count: int = 500) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for i in range(count):
            company_id = random.randint(1, 20)
            record_date = _random_date_in_last_n_months(12)
            month_str = record_date.strftime("%Y-%m")
            month_num = record_date.month

            season = SEASONAL_FACTOR.get(month_num, 1.0)

            # Costs
            operational_cost = round(random.gauss(450_000, 120_000) * season, 2)
            operational_cost = max(100_000, operational_cost)
            marketing_cost = round(random.gauss(70_000, 25_000), 2)
            marketing_cost = max(10_000, marketing_cost)

            # Revenue > costs (usually)
            total_costs = operational_cost + marketing_cost
            revenue = round(total_costs * random.uniform(0.85, 1.45) * season, 2)

            profit = round(revenue - total_costs + random.gauss(0, 15_000), 2)

            records.append({
                "company_id": company_id,
                "month": month_str,
                "operational_cost": operational_cost,
                "marketing_cost": marketing_cost,
                "revenue": revenue,
                "profit": profit,
                "created_at": record_date,
            })
        logger.info("Generated %d finance records", count)
        return records

    # ── Live batch (small, timestamped now) ──────────────────────────────
    def generate_live_batch(
        self,
        customers: int = 5,
        employees: int = 5,
        sales: int = 10,
        finance: int = 3,
    ) -> dict[str, list[dict[str, Any]]]:
        """Generate a small 'real-time' batch with created_at = now."""
        now = datetime.now(timezone.utc)

        def _stamp(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
            for r in records:
                r["created_at"] = now
            return records

        return {
            "customers": _stamp(self.generate_customers(customers)),
            "employees": _stamp(self.generate_employees(employees)),
            "sales": _stamp(self.generate_sales(sales)),
            "finance": _stamp(self.generate_finance(finance)),
        }
