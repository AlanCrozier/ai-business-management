from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

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

def get_sheets_service():
    service = SheetsService.get_instance()
    if not service.client:
        raise HTTPException(status_code=503, detail="Google Sheets Integration is not configured on the server.")
    return service

@router.post("/connect")
async def connect_sheet(req: ConnectSheetRequest, sheets: SheetsService = Depends(get_sheets_service)):
    """Validates the sheet URL and initializes required worksheets."""
    spreadsheet = sheets.get_sheet_by_url(req.sheet_url)
    if not spreadsheet:
        raise HTTPException(status_code=400, detail="Could not access the Google Sheet. Please check the URL and ensure it is shared with the Service Account.")
    
    try:
        sheets.initialize_sheets(spreadsheet)
        return {"success": True, "message": "Sheet connected and initialized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing sheets: {str(e)}")

@router.post("/dashboard")
async def get_dashboard_data(req: ConnectSheetRequest, sheets: SheetsService = Depends(get_sheets_service)):
    """Fetches all data needed to populate the Nexus dashboard from the Google Sheet."""
    try:
        all_data = sheets.get_all_dashboard_data(req.sheet_url, req.uid)
        return {
            "success": True,
            "data": all_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_data(req: SheetSyncRequest, sheets: SheetsService = Depends(get_sheets_service)):
    """Appends data to the appropriate sheet and logs the prediction using ML Models."""
    if not req.data:
        raise HTTPException(status_code=400, detail="Data payload is required.")
        
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Extract prediction data if passed from the frontend ML fallback
    pred_revenue = req.data.pop("predicted_revenue", None)
    pred_profit = req.data.pop("predicted_profit", None)
    anomaly_flag = req.data.pop("anomaly_flag", 1)
    
    ml = MLService.get_instance()
    
    # 1. Save Primary Data & Generate Predictions
    if req.module_type == "sales":
        row = [req.uid, timestamp, req.data.get("product_id"), req.data.get("region"), req.data.get("units_sold"), req.data.get("revenue")]
        sheets.append_row(req.sheet_url, "Sales_Data", row)
        
        if pred_revenue is None:
            dt = datetime.utcnow()
            try:
                pred_revenue = ml.predict_revenue(
                    units_sold=int(req.data.get("units_sold", 0)),
                    region=req.data.get("region", "North"),
                    month=dt.month,
                    day_of_week=dt.weekday()
                )
                pred_profit = ml.predict_profit(
                    operational_cost=pred_revenue * 0.4,
                    marketing_cost=pred_revenue * 0.15,
                    revenue=pred_revenue
                )
            except Exception as e:
                # Fallback if model fails
                pred_revenue = float(req.data.get("revenue", 0)) * 1.12
                pred_profit = pred_revenue * 0.35
                
    elif req.module_type == "customer":
        row = [req.uid, timestamp, req.data.get("customer_id"), req.data.get("age"), req.data.get("city"), req.data.get("membership_level"), req.data.get("lifetime_value")]
        sheets.append_row(req.sheet_url, "Customer_Data", row)
        
        if pred_revenue is None:
            try:
                clv = ml.predict_clv(
                    age=int(req.data.get("age", 30)),
                    gender="Male", # Default
                    city=req.data.get("city", "New York"),
                    total_spent=float(req.data.get("lifetime_value", 0)),
                    membership_level=req.data.get("membership_level", "Silver"),
                    membership_years=2,
                    number_of_purchases=10
                )
                pred_revenue = clv * 1.5
                pred_profit = pred_revenue * 0.4
            except Exception:
                pred_revenue = float(req.data.get("lifetime_value", 0)) * 1.2
                pred_profit = pred_revenue * 0.4
                
    elif req.module_type == "employee":
        row = [req.uid, timestamp, req.data.get("employee_id"), req.data.get("role"), req.data.get("attendance_percent"), req.data.get("years_worked"), req.data.get("performance_score")]
        sheets.append_row(req.sheet_url, "Employee_Data", row)
        
        if pred_revenue is None:
            try:
                perf = ml.predict_employee(
                    age=30,
                    years_worked=int(req.data.get("years_worked", 1)),
                    attendance_percent=float(req.data.get("attendance_percent", 90)),
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
                pred_revenue = float(req.data.get("performance_score", 0)) * 10000
                pred_profit = pred_revenue * 0.25
                
    else:
        raise HTTPException(status_code=400, detail="Invalid module_type")
        
    # Check for random anomalies
    if float(pred_revenue) < 1000:
        anomaly_flag = -1
        
    # 2. Save Prediction Data
    pred_row = [req.uid, timestamp, req.module_type, pred_revenue, pred_profit, anomaly_flag]
    sheets.append_row(req.sheet_url, "Predictions_Data", pred_row)
        
    return {"success": True, "message": "Data synchronized successfully"}
