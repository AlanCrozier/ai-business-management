"""
Google Sheets synchronization router — uses per-user service accounts.

All Google Sheets API calls (gspread) are BLOCKING, so we run them
in a thread pool via asyncio.to_thread() to avoid freezing the event loop.
"""
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from database import get_db
from services.sheets_service import SheetsService
from services.ml_service import MLService

router = APIRouter(prefix="/api/sheets", tags=["Google Sheets Synchronization"])


class SheetSyncRequest(BaseModel):
    uid: str
    sheet_url: str
    module_type: str
    data: Optional[Dict[str, Any]] = None
    

class ConnectSheetRequest(BaseModel):
    uid: str
    sheet_url: str


def _get_user_client(uid: str, db: Session):
    """Helper: get the per-user gspread client (or fallback to shared)."""
    client = SheetsService.get_client_for_user(uid, db)
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Google Sheets integration is not configured. "
                   "Please upload a service account in Settings."
        )
    return client


# ── Helper: run blocking gspread call in thread pool ─────────────────────

def _connect_sheet_sync(client, sheet_url, uid, db):
    """Blocking: open sheet, init tabs, save URL."""
    spreadsheet = SheetsService.get_sheet_by_url(client, sheet_url)
    if not spreadsheet:
        return {"success": False, "error": "Could not access the Google Sheet."}
    
    SheetsService.initialize_sheets(spreadsheet)

    from models.user_account import UserAccount
    account = db.query(UserAccount).filter(UserAccount.firebase_uid == uid).first()
    if account:
        account.sheet_url = sheet_url
        db.commit()

    return {"success": True, "message": "Sheet connected and initialized successfully."}


def _dashboard_sync(client, sheet_url, uid):
    """Blocking: fetch all dashboard data from Google Sheets."""
    return SheetsService.get_all_dashboard_data(client, sheet_url, uid)


def _sync_data_sync(client, sheet_url, uid, module_type, data):
    """Blocking: append data to sheet and log ML predictions."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    pred_revenue = data.pop("predicted_revenue", None)
    pred_profit = data.pop("predicted_profit", None)
    anomaly_flag = data.pop("anomaly_flag", 1)
    
    ml = MLService.get_instance()
    
    if module_type == "sales":
        row = [uid, timestamp, data.get("product_id"), data.get("region"), data.get("units_sold"), data.get("revenue")]
        SheetsService.append_row(client, sheet_url, "Sales_Data", row)
        
        if pred_revenue is None:
            dt = datetime.utcnow()
            try:
                pred_revenue = ml.predict_revenue(
                    units_sold=int(data.get("units_sold", 0)),
                    region=data.get("region", "North"),
                    month=dt.month,
                    day_of_week=dt.weekday()
                )
                pred_profit = ml.predict_profit(
                    operational_cost=pred_revenue * 0.4,
                    marketing_cost=pred_revenue * 0.15,
                    revenue=pred_revenue
                )
            except Exception:
                pred_revenue = float(data.get("revenue", 0)) * 1.12
                pred_profit = pred_revenue * 0.35
                
    elif module_type == "customer":
        row = [uid, timestamp, data.get("customer_id"), data.get("age"), data.get("city"), data.get("membership_level"), data.get("lifetime_value")]
        SheetsService.append_row(client, sheet_url, "Customer_Data", row)
        
        if pred_revenue is None:
            try:
                clv = ml.predict_clv(
                    age=int(data.get("age", 30)),
                    gender="Male",
                    city=data.get("city", "New York"),
                    total_spent=float(data.get("lifetime_value", 0)),
                    membership_level=data.get("membership_level", "Silver"),
                    membership_years=2,
                    number_of_purchases=10
                )
                pred_revenue = clv * 1.5
                pred_profit = pred_revenue * 0.4
            except Exception:
                pred_revenue = float(data.get("lifetime_value", 0)) * 1.2
                pred_profit = pred_revenue * 0.4
                
    elif module_type == "employee":
        row = [uid, timestamp, data.get("employee_id"), data.get("role"), data.get("attendance_percent"), data.get("years_worked"), data.get("performance_score")]
        SheetsService.append_row(client, sheet_url, "Employee_Data", row)
        
        if pred_revenue is None:
            try:
                perf = ml.predict_employee(
                    age=30,
                    years_worked=int(data.get("years_worked", 1)),
                    attendance_percent=float(data.get("attendance_percent", 90)),
                    training_hours=40.0,
                    promotions=0,
                    tasks_completed=100.0,
                    project_success_rate=0.8,
                    manager_rating=4.0,
                    peer_rating=4.0,
                    salary=60000.0
                )
                pred_revenue = perf * 15000
                pred_profit = pred_revenue * 0.25
            except Exception:
                pred_revenue = float(data.get("performance_score", 0)) * 10000
                pred_profit = pred_revenue * 0.25
                
    else:
        return {"success": False, "error": "Invalid module_type"}
        
    if float(pred_revenue) < 1000:
        anomaly_flag = -1
        
    pred_row = [uid, timestamp, module_type, pred_revenue, pred_profit, anomaly_flag]
    SheetsService.append_row(client, sheet_url, "Predictions_Data", pred_row)
        
    return {"success": True, "message": "Data synchronized successfully"}


# ── Endpoints (all run blocking work in thread pool) ─────────────────────

@router.post("/connect")
async def connect_sheet(req: ConnectSheetRequest, db: Session = Depends(get_db)):
    """Validates the sheet URL and initializes required worksheets."""
    client = _get_user_client(req.uid, db)
    result = await asyncio.to_thread(_connect_sheet_sync, client, req.sheet_url, req.uid, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


@router.post("/dashboard")
async def get_dashboard_data(req: ConnectSheetRequest, db: Session = Depends(get_db)):
    """Fetches all data needed to populate the dashboard from the user's Google Sheet."""
    client = _get_user_client(req.uid, db)
    try:
        all_data = await asyncio.to_thread(_dashboard_sync, client, req.sheet_url, req.uid)
        return {"success": True, "data": all_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
async def sync_data(req: SheetSyncRequest, db: Session = Depends(get_db)):
    """Appends data to the appropriate sheet and logs the prediction using ML Models."""
    if not req.data:
        raise HTTPException(status_code=400, detail="Data payload is required.")
    client = _get_user_client(req.uid, db)
    result = await asyncio.to_thread(_sync_data_sync, client, req.sheet_url, req.uid, req.module_type, req.data)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result
