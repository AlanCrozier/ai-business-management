"""
ML Service — loads all 4 pre-trained models and exposes prediction methods.

Label-encoding maps are hard-coded to match the LabelEncoder order used during
training (alphabetical by default in scikit-learn).
"""
from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

logger = logging.getLogger(__name__)

# ── Resolve model directory ─────────────────────────────────────────────────
# models/ sits one level above backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"


# ── Label encoding maps (match sklearn LabelEncoder alphabetical order) ────
GENDER_MAP = {"Female": 0, "Male": 1}
CITY_MAP = {"Bangalore": 0, "Delhi": 2, "Mumbai": 1}  # alphabetical: B=0, M=1, D=2
MEMBERSHIP_MAP = {"Gold": 0, "Platinum": 1, "Silver": 2}  # alphabetical
REGION_MAP = {"East": 0, "North": 1, "South": 2, "West": 3}


class MLService:
    """Singleton service that holds all loaded ML models."""

    _instance: MLService | None = None

    def __init__(self) -> None:
        self.clv_model: Any = None
        self.revenue_model: Any = None
        self.employee_model: Any = None
        self.profit_model: Any = None
        self._loaded = False

    @classmethod
    def get_instance(cls) -> MLService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Model loading ────────────────────────────────────────────────────
    def load_models(self) -> None:
        """Load all .pkl / .joblib models from the models/ directory."""
        if self._loaded:
            return

        logger.info("Loading ML models from %s …", MODELS_DIR)

        # Customer CLV model (file is .plk — typo, but joblib handles it)
        clv_path = MODELS_DIR / "clv_model.pkl"
        if not clv_path.exists():
            clv_path = MODELS_DIR / "random_forest_model.plk"
        if clv_path.exists():
            self.clv_model = joblib.load(clv_path)
            logger.info("✓ CLV model loaded")
        else:
            logger.warning("⚠ CLV model not found")

        # Revenue model
        rev_path = MODELS_DIR / "revenue_model.pkl"
        if rev_path.exists():
            self.revenue_model = joblib.load(rev_path)
            logger.info("✓ Revenue model loaded")
        else:
            logger.warning("⚠ Revenue model not found")

        # Employee model
        emp_path = MODELS_DIR / "employee_model.pkl"
        if emp_path.exists():
            self.employee_model = joblib.load(emp_path)
            logger.info("✓ Employee model loaded")
        else:
            logger.warning("⚠ Employee model not found")

        # Profit model
        profit_path = MODELS_DIR / "profit_model.pkl"
        if not profit_path.exists():
            profit_path = MODELS_DIR / "profit_model.joblib"
        if profit_path.exists():
            self.profit_model = joblib.load(profit_path)
            logger.info("✓ Profit model loaded")
        else:
            logger.warning("⚠ Profit model not found")

        self._loaded = True

    # ── Predictions ──────────────────────────────────────────────────────
    def predict_clv(
        self,
        age: int,
        gender: str,
        city: str,
        total_spent: float,
        membership_level: str,
        membership_years: int,
        number_of_purchases: int,
    ) -> float:
        """Predict customer lifetime value."""
        if self.clv_model is None:
            raise RuntimeError("CLV model not loaded")

        features = np.array([[
            age,
            GENDER_MAP.get(gender, 0),
            CITY_MAP.get(city, 0),
            total_spent,
            MEMBERSHIP_MAP.get(membership_level, 0),
            membership_years,
            number_of_purchases,
        ]])
        prediction = self.clv_model.predict(features)
        return float(prediction[0])

    def predict_revenue(
        self,
        units_sold: int,
        region: str,
        month: int,
        day_of_week: int,
    ) -> float:
        """Predict revenue for a sale."""
        if self.revenue_model is None:
            raise RuntimeError("Revenue model not loaded")

        features = np.array([[
            units_sold,
            REGION_MAP.get(region, 0),
            month,
            day_of_week,
        ]])
        prediction = self.revenue_model.predict(features)
        return float(prediction[0])

    def predict_employee(
        self,
        age: int,
        years_worked: int,
        attendance_percent: float,
        training_hours: float,
        promotions: int,
        tasks_completed: float,
        project_success_rate: float,
        manager_rating: float,
        peer_rating: float,
        salary: float,
    ) -> float:
        """Predict employee performance score."""
        if self.employee_model is None:
            raise RuntimeError("Employee model not loaded")

        features = np.array([[
            age,
            years_worked,
            attendance_percent,
            training_hours,
            promotions,
            tasks_completed,
            project_success_rate,
            manager_rating,
            peer_rating,
            salary,
        ]])
        prediction = self.employee_model.predict(features)
        return float(prediction[0])

    def predict_profit(
        self,
        operational_cost: float,
        marketing_cost: float,
        revenue: float,
    ) -> float:
        """Predict net profit."""
        if self.profit_model is None:
            raise RuntimeError("Profit model not loaded")

        features = np.array([[
            operational_cost,
            marketing_cost,
            revenue,
        ]])
        prediction = self.profit_model.predict(features)
        return float(prediction[0])
