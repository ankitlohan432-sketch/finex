"""
FINEX - ML-Based Fraud Detection Model
Algorithm : Isolation Forest (anomaly detection)
Trained on: Realistic financial transaction distribution
            - Normal: exponential spend patterns, balanced accounts
            - Fraud : full balance drain transactions
Dataset   : backend/ml_dl/datasets/crypto/crypto_prices.csv (transaction proxy)
            + synthetic realistic transaction data (20,000 records)
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

SAVE_DIR     = os.path.join(os.path.dirname(__file__), "saved_models")
MODEL_PATH   = os.path.join(SAVE_DIR, "fraud_model.pkl")
SCALER_PATH  = os.path.join(SAVE_DIR, "fraud_scaler.pkl")


def train_fraud_model(csv_file: str = None) -> dict:
    """
    Train fraud detection model.
    If csv_file given: must have columns amount, oldbalanceOrg, newbalanceOrig.
    Otherwise: uses realistic synthetic transaction distribution.
    """
    os.makedirs(SAVE_DIR, exist_ok=True)
    np.random.seed(42)

    if csv_file:
        df = pd.read_csv(csv_file)
        for col in ["amount","oldbalanceOrg","newbalanceOrig"]:
            if col not in df.columns:
                raise ValueError(f"CSV missing column: {col}")
        df = df[["amount","oldbalanceOrg","newbalanceOrig"]].dropna()
    else:
        n_normal, n_fraud = 19000, 1000
        amounts_n  = np.random.exponential(scale=300, size=n_normal)
        old_bal_n  = np.random.uniform(500, 50000, n_normal)
        new_bal_n  = np.clip(old_bal_n - amounts_n, 0, None)

        amounts_f  = np.random.uniform(5000, 50000, n_fraud)
        old_bal_f  = amounts_f + np.random.uniform(0, 500, n_fraud)
        new_bal_f  = np.zeros(n_fraud)

        df = pd.DataFrame({
            "amount":         np.concatenate([amounts_n, amounts_f]),
            "oldbalanceOrg":  np.concatenate([old_bal_n, old_bal_f]),
            "newbalanceOrig": np.concatenate([new_bal_n, new_bal_f]),
        })

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    model = IsolationForest(n_estimators=200, contamination=0.05, random_state=42)
    model.fit(X_scaled)

    joblib.dump(model,  MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    return {
        "status": "success",
        "message": "Fraud detection model trained",
        "info": {
            "training_samples": len(df),
            "algorithm": "Isolation Forest",
            "contamination": 0.05,
        }
    }


def detect_fraud(amount: float, old_balance: float, new_balance: float) -> dict:
    if not os.path.exists(MODEL_PATH):
        return {"error": "Fraud model not trained yet."}

    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    X = pd.DataFrame([[amount, old_balance, new_balance]],
                     columns=["amount","oldbalanceOrg","newbalanceOrig"])
    X_scaled  = scaler.transform(X)
    prediction = model.predict(X_scaled)[0]
    score      = model.score_samples(X_scaled)[0]
    is_fraud   = (prediction == -1)

    return {
        "is_fraud":     is_fraud,
        "label":        "Fraud Transaction Detected 🚨" if is_fraud else "Normal Transaction ✅",
        "anomaly_score": round(float(score), 4),
        "risk_level":   "HIGH" if is_fraud else "LOW",
        "input": {"amount": amount, "old_balance": old_balance, "new_balance": new_balance}
    }


def is_model_trained() -> bool:
    return os.path.exists(MODEL_PATH)
