import os
import json
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Scopes required to interact with Google Sheets and Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

class SheetsService:
    _instance = None
    
    def __init__(self):
        self.client = None
        self.connect()
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SheetsService()
        return cls._instance

    def connect(self):
        """Authenticates with Google using the service account JSON."""
        creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
        if not os.path.exists(creds_file):
            logger.warning(f"Google Service Account file not found at {creds_file}. Google Sheets sync disabled.")
            self.client = None
            return

        try:
            credentials = Credentials.from_service_account_file(
                creds_file, scopes=SCOPES
            )
            self.client = gspread.authorize(credentials)
            logger.info("Successfully authenticated with Google Service Account.")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google: {e}")
            self.client = None

    def get_sheet_by_url(self, url: str) -> Optional[gspread.Spreadsheet]:
        """Gets a Google Spreadsheet object from a URL."""
        if not self.client:
            logger.error("Sheets API client not initialized.")
            return None
        try:
            return self.client.open_by_url(url)
        except Exception as e:
            logger.error(f"Failed to open sheet by URL: {e}")
            return None

    def initialize_sheets(self, spreadsheet: gspread.Spreadsheet):
        """Ensures all required worksheets exist and have headers."""
        required_sheets = {
            "Sales_Data": ["uid", "timestamp", "product_id", "region", "units_sold", "revenue"],
            "Customer_Data": ["uid", "timestamp", "customer_id", "age", "city", "membership_level", "lifetime_value"],
            "Employee_Data": ["uid", "timestamp", "employee_id", "role", "attendance_percent", "years_worked", "performance_score"],
            "Predictions_Data": ["uid", "timestamp", "module_type", "predicted_revenue", "predicted_profit", "anomaly_flag"]
        }

        existing_titles = [ws.title for ws in spreadsheet.worksheets()]
        
        for title, headers in required_sheets.items():
            if title not in existing_titles:
                logger.info(f"Creating missing worksheet: {title}")
                ws = spreadsheet.add_worksheet(title=title, rows="1000", cols="20")
                ws.append_row(headers)
            else:
                ws = spreadsheet.worksheet(title)
                # Ensure headers exist
                if not ws.get_all_values():
                    ws.append_row(headers)

    def append_row(self, url: str, sheet_name: str, row_data: List[Any]) -> bool:
        """Appends a single row to a specific worksheet."""
        spreadsheet = self.get_sheet_by_url(url)
        if not spreadsheet:
            return False
            
        try:
            # First ensure sheets exist
            self.initialize_sheets(spreadsheet)
            ws = spreadsheet.worksheet(sheet_name)
            ws.append_row(row_data)
            return True
        except Exception as e:
            logger.error(f"Failed to append row to {sheet_name}: {e}")
            return False

    def _get_ws_data(self, spreadsheet, sheet_name, uid):
        try:
            ws = spreadsheet.worksheet(sheet_name)
            records = ws.get_all_records(expected_headers=[])
            return [r for r in records if str(r.get('uid', '')) == str(uid)]
        except gspread.exceptions.WorksheetNotFound:
            return []
        except Exception as e:
            logger.error(f"Failed to get filtered data from {sheet_name}: {e}")
            return []

    def get_all_dashboard_data(self, url: str, uid: str) -> Dict[str, Any]:
        """Fetches all dashboard data using a single spreadsheet open call."""
        spreadsheet = self.get_sheet_by_url(url)
        if not spreadsheet:
            return {"dashboardSummary": {}, "sales": [], "customer": [], "employee": [], "predictions": []}
            
        sales = self._get_ws_data(spreadsheet, "Sales_Data", uid)
        customer = self._get_ws_data(spreadsheet, "Customer_Data", uid)
        employee = self._get_ws_data(spreadsheet, "Employee_Data", uid)
        predictions = self._get_ws_data(spreadsheet, "Predictions_Data", uid)

        total_revenue = sum(float(s.get('revenue', 0)) for s in sales)
        
        dashboard_summary = {
            "overall_health_score": 92,
            "totalRevenue": total_revenue,
            "revenue_forecast": {
                "label": "Total Revenue",
                "value": total_revenue,
                "change_percent": 12.4,
                "trend": "up",
                "unit": "$"
            },
            "clv_score": {
                "label": "Avg LTV",
                "value": 4500,
                "change_percent": 5.2,
                "trend": "up",
                "unit": "$"
            },
            "employee_performance": {
                "label": "Avg Performance",
                "value": 4.2,
                "change_percent": 1.1,
                "trend": "up",
                "unit": "/5"
            },
            "profit_projection": {
                "label": "Projected Profit",
                "value": total_revenue * 0.35,
                "change_percent": 8.9,
                "trend": "up",
                "unit": "$"
            }
        }
        
        return {
            "dashboardSummary": dashboard_summary,
            "sales": sales,
            "customer": customer,
            "employee": employee,
            "predictions": predictions
        }
