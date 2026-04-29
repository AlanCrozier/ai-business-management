"""
FastAPI application entry point.
Loads ML models on startup, registers routers, configures CORS.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from services.ml_service import MLService
from routers import predict, dashboard, data_router, sheets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables, load ML models, auto-seed if empty."""
    # Create database tables (includes new dataset tables)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

    # Load all ML models into memory
    ml = MLService.get_instance()
    ml.load_models()
    logger.info("ML models loaded successfully.")

    # Auto-seed dataset tables on first run (if empty)
    from sqlalchemy.orm import Session
    from models.dataset_models import CustomerRecord
    from services.data_generator import DataGeneratorService
    from models.dataset_models import EmployeeRecord, SalesRecord, FinanceRecord

    db = Session(bind=engine)
    try:
        count = db.query(CustomerRecord).count()
        if count == 0:
            logger.info("Empty dataset tables detected — auto-seeding with 500 records each…")
            gen = DataGeneratorService()
            for model_cls, data in [
                (CustomerRecord, gen.generate_customers(500)),
                (EmployeeRecord, gen.generate_employees(500)),
                (SalesRecord, gen.generate_sales(500)),
                (FinanceRecord, gen.generate_finance(500)),
            ]:
                db.bulk_save_objects([model_cls(**r) for r in data])
            db.commit()
            logger.info("Auto-seed complete — 2 000 total records inserted.")
        else:
            logger.info("Dataset tables already contain data (%d customers). Skipping seed.", count)
    except Exception as e:
        logger.warning("Auto-seed skipped due to error: %s", e)
        db.rollback()
    finally:
        db.close()

    yield  # app runs here

    logger.info("Shutting down…")


app = FastAPI(
    title="AI Enterprise Analytics API",
    description="Predictive Insights for CLV, Revenue, Employee Performance & Profit",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(predict.router)
app.include_router(dashboard.router)
app.include_router(data_router.router)
app.include_router(sheets.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "AI Enterprise Analytics API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Root"])
def health():
    ml = MLService.get_instance()
    return {
        "status": "ok",
        "models_loaded": {
            "clv": ml.clv_model is not None,
            "revenue": ml.revenue_model is not None,
            "employee": ml.employee_model is not None,
            "profit": ml.profit_model is not None,
        },
    }
