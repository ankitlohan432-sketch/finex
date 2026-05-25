"""
FINEX - Expense Prediction Model (ML)
Algorithm : Decision Tree Regressor
Trained on: Realistic income/savings/expense distribution (5000 samples)
            Based on real financial ratios (40-75% expense ratio)
Dataset   : Synthetic but statistically realistic (upload your own CSV to improve)
            CSV format needed: income, savings, expense  (all numbers)
"""

import os
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

SAVE_DIR   = os.path.join(os.path.dirname(__file__), "saved_models")
MODEL_PATH = os.path.join(SAVE_DIR, "expense_model.pkl")


def train_expense_model(csv_file: str = None) -> dict:
    """
    Train expense prediction model.
    Upload your own CSV (income, savings, expense) for better accuracy.
    If no file given, uses realistic synthetic data.
    """
    os.makedirs(SAVE_DIR, exist_ok=True)

    if csv_file:
        df = pd.read_csv(csv_file)
        for col in ["income","savings","expense"]:
            if col not in df.columns:
                raise ValueError(f"CSV missing column: {col}")
        df = df[["income","savings","expense"]].dropna()
    else:
        np.random.seed(42)
        n       = 5000
        income  = np.random.randint(30000, 200000, n).astype(float)
        savings = income * np.random.uniform(0.05, 0.35, n)
        expense = income * np.random.uniform(0.40, 0.75, n) + np.random.normal(0, 2000, n)
        expense = np.clip(expense, 5000, income * 0.95)
        df = pd.DataFrame({"income": income, "savings": savings, "expense": expense})

    X = df[["income","savings"]]
    y = df["expense"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = DecisionTreeRegressor(max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    joblib.dump(model, MODEL_PATH)
    return {
        "status": "success",
        "message": "Expense prediction model trained",
        "metrics": {
            "mean_absolute_error": round(float(mean_absolute_error(y_test, y_pred)), 2),
            "r2_score":            round(float(r2_score(y_test, y_pred)), 4),
            "training_samples":    int(len(X_train)),
        }
    }


def predict_expense(income: float, savings: float) -> dict:
    if not os.path.exists(MODEL_PATH):
        return {"error": "Expense model not trained yet."}
    model = joblib.load(MODEL_PATH)
    pred = model.predict(pd.DataFrame([[income, savings]], columns=["income","savings"]))[0]
    return {
        "predicted_expense": round(float(pred), 2),
        "input": {"income": income, "savings": savings}
    }


def is_model_trained() -> bool:
    return os.path.exists(MODEL_PATH)
