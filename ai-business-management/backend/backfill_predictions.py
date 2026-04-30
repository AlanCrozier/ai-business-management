import json
from datetime import datetime
from database import SessionLocal
from models.user_account import UserAccount
from services.sheets_service import SheetsService
from services.ml_service import MLService

db = SessionLocal()
accounts = db.query(UserAccount).filter(UserAccount.sheet_url != None).all()
ml = MLService.get_instance()

if not accounts:
    print("No users with connected Google Sheets found.")

for acct in accounts:
    uid = acct.firebase_uid
    print(f"\nProcessing backfill for user: {uid}")
    
    try:
        client = SheetsService.get_client_for_user(uid, db)
        if not client:
            print(f"  -> Failed to get Google Sheets client for {uid}. Skipping.")
            continue
            
        spreadsheet = client.open_by_url(acct.sheet_url)
        sales_ws = spreadsheet.worksheet("Sales_Data")
        preds_ws = spreadsheet.worksheet("Predictions_Data")
        
        sales_data = sales_ws.get_all_records()
        preds_data = preds_ws.get_all_records()
        
        # Find timestamps that don't have predictions
        existing_preds = {str(p.get("Timestamp")): True for p in preds_data}
        
        new_preds = []
        
        for row in sales_data:
            ts = str(row.get("Timestamp"))
            if not ts or ts in existing_preds:
                continue
                
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                dt = datetime.utcnow()
                
            try:
                units = int(row.get("Units_Sold", 0))
                region = row.get("Region", "North")
                rev = ml.predict_revenue(units_sold=units, region=region, month=dt.month, day_of_week=dt.weekday())
                profit = ml.predict_profit(operational_cost=rev*0.4, marketing_cost=rev*0.15, revenue=rev)
            except Exception as e:
                print("  -> ML error:", e)
                rev = float(row.get("Revenue", 0)) * 1.12
                profit = rev * 0.35
                
            anomaly = -1 if float(rev) < 1000 else 1
            new_preds.append([uid, ts, "sales", rev, profit, anomaly])
        
        if new_preds:
            print(f"  -> Adding {len(new_preds)} new predictions...")
            preds_ws.append_rows(new_preds)
            print("  -> Done!")
        else:
            print("  -> No missing predictions found.")
            
    except Exception as e:
        print(f"  -> Error processing user {uid}: {e}")

db.close()
