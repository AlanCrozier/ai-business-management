# ==============================
# 1️⃣ IMPORT LIBRARIES
# ==============================
import pandas as pd
import numpy as np
import time
from datetime import datetime
from sqlalchemy import create_engine
import joblib
# ==============================
# 2️⃣ DATABASE CONNECTION
# ==============================
engine = create_engine("sqlite:///mini_project.db")

# ==============================
# 3️⃣ LOAD MODELS
# ==============================
revenue_model = joblib.load("models/revenue_model.pkl")
profit_model = joblib.load("models/profit_model.joblib")
customer_model = joblib.load("models/clv_model.pkl")
employee_model = joblib.load("models/employee_model.pkl")
# anomaly_model = joblib.load("models/enterprise_anomaly_model.pkl")  # File not found

# ==============================
# 4️⃣ DATA GENERATION
# ==============================
def generate_sales_data(customer_ids, n=10):
    regions = ["North","South","East","West"]
    products = ["P101","P102","P103","P104"]

    data = []

    for i in range(n):
        units = np.random.randint(1,5)
        price = np.random.choice([50,100,200])
        marketing_cost = np.random.uniform(10, 50)
        operational_cost = np.random.uniform(20, 100)

        data.append({
            "date": datetime.now(),
            "customer_id": customer_ids[i],
            "product_id": np.random.choice(products),
            "region": np.random.choice(regions),
            "units_sold": units,
            "revenue": units * price,
            "marketing_cost": marketing_cost,
            "operational_cost": operational_cost
        })

    return pd.DataFrame(data)


def generate_customer_data(customer_ids, n=10):
    cities = ["Delhi","Mumbai","Bangalore"]
    membership = ["Silver","Gold","Platinum"]
    genders = ["Male", "Female"]

    data = []

    for i in range(n):
        purchases = np.random.randint(1,10)
        spent = purchases * np.random.randint(100,500)

        weight = {"Silver":1.0,"Gold":1.3,"Platinum":1.7}
        m = np.random.choice(membership)

        data.append({
            "customer_id": customer_ids[i],
            "age": np.random.randint(18,60),
            "gender": np.random.choice(genders),
            "city": np.random.choice(cities),
            "total_spent": spent,
            "membership_level": m,
            "membership_years": np.random.randint(0,5),
            "number_of_purchases": purchases,
            "lifetime_value": spent * weight[m]
        })

    return pd.DataFrame(data)


def generate_employee_data(n=5):
    roles = ["Intern","Junior","Senior","Manager"]

    data = []

    for _ in range(n):
        years = np.random.randint(0,10)
        attendance = np.random.uniform(80,100)

        performance = (
            0.4*(attendance/100) +
            0.3*(years/10) +
            0.3*np.random.uniform(0.5,1)
        )

        data.append({
            "employee_id": np.random.randint(100000,999999),
            "age": np.random.randint(22,55),
            "years_worked": years,
            "attendance_percent": attendance,
            "training_hours": np.random.randint(10,100),
            "promotions": np.random.randint(0,5),
            "tasks_completed": np.random.randint(50,200),
            "project_success_rate": np.random.uniform(0.7,1.0),
            "manager_rating": np.random.uniform(3,5),
            "peer_rating": np.random.uniform(3,5),
            "salary": np.random.randint(30000,120000),
            "role": np.random.choice(roles),
            "performance_score": round(1 + performance*4, 2)
        })

    return pd.DataFrame(data)

# ==============================
# 5️⃣ INSERT FUNCTION
# ==============================
def insert_to_db(df, table_name):
    try:
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
    except Exception as e:
        print("Insert error:", e)

# ==============================
# 6️⃣ FETCH DATA
# ==============================
def fetch_latest_data():
    sales = pd.read_sql("SELECT * FROM sales ORDER BY date DESC LIMIT 50", engine)
    customers = pd.read_sql("SELECT * FROM customers LIMIT 50", engine)
    employees = pd.read_sql("SELECT * FROM employees LIMIT 50", engine)

    return sales, customers, employees

# ==============================
# 7️⃣ PREPROCESSING
# ==============================
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import pandas as pd

def preprocess_sales(df):
    # Extract date features
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    
    # Create region_encoded
    le = LabelEncoder()
    df['region_encoded'] = le.fit_transform(df['region'])
    
    return df[['units_sold', 'region_encoded', 'month', 'day_of_week']]

def preprocess_customers(df):
    df = df.copy()
    
    # Encode categorical features
    le_gender = LabelEncoder()
    le_city = LabelEncoder()
    le_membership = LabelEncoder()
    
    df['gender'] = le_gender.fit_transform(df['gender'])
    df['city'] = le_city.fit_transform(df['city'])
    df['membership_level'] = le_membership.fit_transform(df['membership_level'])
    
    return df[['age', 'gender', 'city', 'total_spent', 'membership_level', 'membership_years', 'number_of_purchases']]

# ==============================
# 8️⃣ PREDICTIONS
# ==============================
def predict_all(sales, customers, employees):

    # Revenue
    sales_X = preprocess_sales(sales)
    sales["predicted_revenue"] = revenue_model.predict(sales_X)

    # Profit
    sales["predicted_profit"] = profit_model.predict(
        sales[["operational_cost", "marketing_cost", "revenue"]]
    )

    # Customer
    customer_X = preprocess_customers(customers)
    customers["predicted_ltv"] = customer_model.predict(customer_X)

    # Employee
    employees["predicted_performance"] = employee_model.predict(
        employees[["age", "years_worked", "attendance_percent", "training_hours", "promotions", "tasks_completed", "project_success_rate", "manager_rating", "peer_rating", "salary"]]
    )

    return sales, customers, employees

# ==============================
# 9️⃣ ANOMALY DETECTION
# ==============================
def detect_anomalies(sales):
    sales["anomaly"] = anomaly_model.predict(
        sales[["units_sold","revenue"]]
    )
    return sales[sales["anomaly"] == -1]

# ==============================
# 🔟 FORECASTING
# ==============================
def forecast_revenue(sales):
    sales = sales.sort_values("date")
    sales["trend"] = sales["revenue"].rolling(5).mean()
    return sales["trend"].iloc[-1]

# ==============================
# 11️⃣ BUSINESS ANALYSIS
# ==============================
def analyze(sales, customers, employees):

    future_revenue = forecast_revenue(sales)

    insights = []

    if future_revenue < 5000:
        insights.append("⚠️ Revenue may drop")

    if customers["predicted_ltv"].mean() < 3000:
        insights.append("⚠️ Customer value low")

    if employees["predicted_performance"].mean() < 3:
        insights.append("⚠️ Employee performance low")

    return future_revenue, insights

# ==============================
# 12️⃣ MAIN LOOP
# ==============================
import signal
import sys

def signal_handler(sig, frame):
    print("\nExiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    try:
        # Generate shared customer IDs
        customer_ids = np.random.randint(5000,8000,10)

        # Generate data
        sales_df = generate_sales_data(customer_ids,10)
        customer_df = generate_customer_data(customer_ids,10)
        employee_df = generate_employee_data(5)

        # Insert
        insert_to_db(sales_df,"sales")
        insert_to_db(customer_df,"customers")
        insert_to_db(employee_df,"employees")

        # Fetch latest
        sales, customers, employees = fetch_latest_data()

        # Predict
        sales, customers, employees = predict_all(sales, customers, employees)

        # Detect anomalies
        # anomalies = detect_anomalies(sales)

        # Analysis
        future_revenue, insights = analyze(sales, customers, employees)

        # Output
        print("\n===== REAL-TIME AI SYSTEM =====")
        print("Time:", datetime.now())
        print("Future Revenue:", future_revenue)
        # print("Anomalies:", len(anomalies))

        print("\nInsights:")
        for i in insights:
            print("-", i)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)