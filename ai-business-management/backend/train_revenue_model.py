"""
Train a revenue prediction model from the master sales dataset.
Saves the model as models/revenue_model.pkl.

Run: python train_revenue_model.py
"""
import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "sale_model" / "master_sales_dataset.csv"
# Also try Data subfolder
if not DATA_PATH.exists():
    DATA_PATH = BASE_DIR / "sale_model" / "Data" / "sales_dataset.csv"
OUTPUT_PATH = BASE_DIR / "models" / "revenue_model.pkl"


def main():
    print(f"Loading data from {DATA_PATH} …")
    if not DATA_PATH.exists():
        print(f"ERROR: Data file not found at {DATA_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Feature engineering
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.month
        df["day_of_week"] = df["date"].dt.dayofweek
    else:
        df["month"] = 6
        df["day_of_week"] = 2

    # Encode region
    le_region = LabelEncoder()
    if "region" in df.columns:
        df["region_encoded"] = le_region.fit_transform(df["region"])
    else:
        df["region_encoded"] = 0

    # Select features
    feature_cols = ["units_sold", "region_encoded", "month", "day_of_week"]
    target_col = "revenue"

    # Verify columns exist
    for col in feature_cols + [target_col]:
        if col not in df.columns:
            print(f"ERROR: Column '{col}' not found. Available: {list(df.columns)}")
            sys.exit(1)

    X = df[feature_cols]
    y = df[target_col]

    print(f"Features: {feature_cols}")
    print(f"Target: {target_col}")
    print(f"X shape: {X.shape}, y shape: {y.shape}")

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        oob_score=True,
    )
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"\nRevenue Model MAE : {mae:.2f}")
    print(f"Revenue Model R²  : {r2:.4f}")
    print(f"OOB Score         : {model.oob_score_:.4f}")

    # Save
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUTPUT_PATH)
    print(f"\n✓ Model saved to {OUTPUT_PATH}")
    print(f"  Region encoding: {dict(zip(le_region.classes_, le_region.transform(le_region.classes_)))}")


if __name__ == "__main__":
    main()
