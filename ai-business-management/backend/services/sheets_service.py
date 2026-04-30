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
    """Shared/fallback Sheets client using the server-level service_account.json."""
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
        """Authenticates with Google using the server-level service account JSON."""
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
            logger.info("Successfully authenticated with server-level Google Service Account.")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google: {e}")
            self.client = None

    # ── Per-User Client ──────────────────────────────────────────────────

    _user_clients: Dict[str, gspread.Client] = {}

    @classmethod
    def get_client_for_user(cls, uid: str, db_session) -> Optional[gspread.Client]:
        """
        Returns a gspread client authenticated with the user's own service account.
        Falls back to the shared server client if the user has no SA configured.
        """
        from models.user_account import UserAccount
        from services import crypto_service

        # Check cache first
        if uid in cls._user_clients:
            return cls._user_clients[uid]

        # Look up encrypted SA from DB
        account = db_session.query(UserAccount).filter(
            UserAccount.firebase_uid == uid
        ).first()

        if not account or not account.sa_encrypted:
            # Fall back to shared server client
            instance = cls.get_instance()
            return instance.client

        try:
            sa_json_str = crypto_service.decrypt(account.sa_encrypted)
            sa_info = json.loads(sa_json_str)

            credentials = Credentials.from_service_account_info(
                sa_info, scopes=SCOPES
            )
            client = gspread.authorize(credentials)
            cls._user_clients[uid] = client
            logger.info("Created per-user gspread client for UID=%s (project=%s)", uid, sa_info.get("project_id"))
            return client
        except Exception as e:
            logger.error("Failed to create per-user client for UID=%s: %s", uid, e)
            # Fall back to shared
            instance = cls.get_instance()
            return instance.client

    @classmethod
    def invalidate_user_client(cls, uid: str):
        """Remove a cached per-user client (e.g. after SA update/delete)."""
        cls._user_clients.pop(uid, None)

    # ── Sheet Operations (work with any gspread client) ──────────────────

    @staticmethod
    def get_sheet_by_url(client: gspread.Client, url: str) -> Optional[gspread.Spreadsheet]:
        """Gets a Google Spreadsheet object from a URL using the given client."""
        if not client:
            logger.error("Sheets API client not initialized.")
            return None
        try:
            return client.open_by_url(url)
        except Exception as e:
            logger.error(f"Failed to open sheet by URL: {e}")
            return None

    @staticmethod
    def initialize_sheets(spreadsheet: gspread.Spreadsheet):
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

    @staticmethod
    def append_row(client: gspread.Client, url: str, sheet_name: str, row_data: List[Any]) -> bool:
        """Appends a single row to a specific worksheet."""
        spreadsheet = SheetsService.get_sheet_by_url(client, url)
        if not spreadsheet:
            return False
            
        try:
            SheetsService.initialize_sheets(spreadsheet)
            ws = spreadsheet.worksheet(sheet_name)
            ws.append_row(row_data)
            return True
        except Exception as e:
            logger.error(f"Failed to append row to {sheet_name}: {e}")
            return False

    @staticmethod
    def _get_ws_data(spreadsheet, sheet_name, uid):
        try:
            ws = spreadsheet.worksheet(sheet_name)
            records = ws.get_all_records(expected_headers=[])
            return [r for r in records if str(r.get('uid', '')) == str(uid)]
        except gspread.exceptions.WorksheetNotFound:
            return []
        except Exception as e:
            logger.error(f"Failed to get filtered data from {sheet_name}: {e}")
            return []

    @staticmethod
    def get_all_dashboard_data(client: gspread.Client, url: str, uid: str) -> Dict[str, Any]:
        """Fetches all dashboard data using the given client."""
        spreadsheet = SheetsService.get_sheet_by_url(client, url)
        if not spreadsheet:
            return {"dashboardSummary": {}, "sales": [], "customer": [], "employee": [], "predictions": []}
            
        sales = SheetsService._get_ws_data(spreadsheet, "Sales_Data", uid)
        customer = SheetsService._get_ws_data(spreadsheet, "Customer_Data", uid)
        employee = SheetsService._get_ws_data(spreadsheet, "Employee_Data", uid)
        predictions = SheetsService._get_ws_data(spreadsheet, "Predictions_Data", uid)

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
