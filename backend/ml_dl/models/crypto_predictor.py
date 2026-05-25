"""
FINEX - Crypto Price Prediction Model (v2 - No Overfitting)
============================================================
WHAT CHANGED AND WHY:
  OLD (broken): Random Forest predicting Close from Open+High+Low (same candle).
      -> Data leakage: High/Low are only known AFTER the candle closes.
      -> Fake R²≈0.99 — model just memorizes intra-candle relationships.

  NEW (correct): Predicts NEXT DAY direction + % change using only PAST data:
      - Lag returns (1d, 3d, 7d, 14d)
      - Rolling volatility (7d, 30d)
      - Price vs moving averages
      - RSI (14-day)
      - Volume ratio
      - Typical daily range

Validation: Walk-forward TimeSeriesSplit (no future leakage)
Expected accuracy: ~51-54% direction (crypto markets are highly random short-term)

Dataset: backend/ml_dl/datasets/crypto/btc_daily.csv
         (extends to other symbols when multi-symbol CSV provided)
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

SAVE_DIR    = os.path.join(os.path.dirname(__file__), "saved_models")
CLF_PATH    = os.path.join(SAVE_DIR, "crypto_clf.pkl")
REG_PATH    = os.path.join(SAVE_DIR, "crypto_reg.pkl")
SCALER_PATH = os.path.join(SAVE_DIR, "crypto_scaler.pkl")
MODEL_PATH  = os.path.join(SAVE_DIR, "crypto_model.pkl")   # backward compat

DATASET = os.path.join(os.path.dirname(__file__), "../datasets/crypto/btc_daily.csv")

SUPPORTED_SYMBOLS = ["BTC", "ETH", "BNB", "ADA", "XRP", "DOGE", "LTC", "SOL", "MATIC", "DOT"]

FEAT_COLS = [
    'return_1d', 'return_3d', 'return_7d', 'return_14d',
    'vol_7d', 'vol_30d',
    'price_to_ma7', 'price_to_ma30',
    'ma7_to_ma30', 'rsi',
    'vol_ratio', 'hl_range'
]


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build lag-based features from daily OHLCV crypto data.
    All features use only PAST information (no leakage).
    """
    df = df.copy()

    close_col = next((c for c in df.columns if c.lower() == 'close'), 'Close')
    df = df.rename(columns={close_col: 'Close'})

    # Returns (log or simple)
    df['return_1d']  = df['Close'].pct_change(1)
    df['return_3d']  = df['Close'].pct_change(3)
    df['return_7d']  = df['Close'].pct_change(7)
    df['return_14d'] = df['Close'].pct_change(14)

    # Rolling volatility
    df['vol_7d']  = df['return_1d'].rolling(7).std()
    df['vol_30d'] = df['return_1d'].rolling(30).std()

    # Moving average ratios
    df['ma7']  = df['Close'].rolling(7).mean()
    df['ma30'] = df['Close'].rolling(30).mean()
    df['price_to_ma7']  = df['Close'] / df['ma7']  - 1
    df['price_to_ma30'] = df['Close'] / df['ma30'] - 1
    df['ma7_to_ma30']   = df['ma7']   / df['ma30'] - 1

    # RSI (14-day)
    delta = df['Close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    # Volume ratio
    vol_col = next((c for c in df.columns if c.lower() == 'volume'), None)
    if vol_col and df[vol_col].sum() > 0:
        df['vol_ratio'] = df[vol_col] / df[vol_col].rolling(20).mean()
    else:
        df['vol_ratio'] = 1.0

    # High-Low range
    high_col = next((c for c in df.columns if c.lower() == 'high'), None)
    low_col  = next((c for c in df.columns if c.lower() == 'low'),  None)
    if high_col and low_col:
        df['hl_range'] = (df[high_col] - df[low_col]) / df['Close']
    else:
        df['hl_range'] = df['vol_7d'].fillna(0) * 2   # proxy if H/L unavailable

    # TARGET: next day normalized return
    df['next_return']    = df['Close'].pct_change(1).shift(-1)
    df['next_direction'] = (df['next_return'] > 0).astype(int)

    return df.dropna()


def train_crypto_model(csv_file: str = None, symbols: list = None) -> dict:
    """
    Train crypto prediction model.

    Parameters
    ----------
    csv_file : str, optional
        Custom CSV. Expected columns: Date, Close (minimum).
        Optional: Open, High, Low, Volume, Symbol.
    symbols : list, optional
        Filter to specific symbols if CSV has a Symbol column.
    """
    os.makedirs(SAVE_DIR, exist_ok=True)

    src = csv_file or DATASET
    df  = pd.read_csv(src)

    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    # Filter by symbol if available
    if 'Symbol' in df.columns or 'symbol' in df.columns:
        sym_col = 'Symbol' if 'Symbol' in df.columns else 'symbol'
        filter_syms = symbols or ["BTC", "ETH", "BNB", "ADA", "XRP"]
        df = df[df[sym_col].isin(filter_syms)]

    # Parse date
    date_col = next((c for c in df.columns if c.lower() in ('date', 'datetime')), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.set_index(date_col).sort_index()

    data = _engineer_features(df)

    if data.empty or len(data) < 100:
        return {"error": "Not enough data. Need at least 100 daily rows after feature engineering."}

    X     = data[FEAT_COLS]
    y_dir = data['next_direction']
    y_ret = data['next_return']

    # Walk-forward CV
    tscv = TimeSeriesSplit(n_splits=5)
    dir_scores, ret_maes = [], []

    for train_idx, test_idx in tscv.split(X):
        X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
        sc = StandardScaler().fit(X_tr)

        clf_cv = GradientBoostingClassifier(
            n_estimators=100, max_depth=3, learning_rate=0.05,
            subsample=0.8, random_state=42
        )
        clf_cv.fit(sc.transform(X_tr), y_dir.iloc[train_idx])
        dir_scores.append(accuracy_score(y_dir.iloc[test_idx], clf_cv.predict(sc.transform(X_te))))

        reg_cv = GradientBoostingRegressor(
            n_estimators=100, max_depth=3, learning_rate=0.05,
            subsample=0.8, random_state=42
        )
        reg_cv.fit(sc.transform(X_tr), y_ret.iloc[train_idx])
        ret_maes.append(mean_absolute_error(y_ret.iloc[test_idx], reg_cv.predict(sc.transform(X_te))))

    # Final model on all data
    scaler   = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)

    clf = GradientBoostingClassifier(
        n_estimators=100, max_depth=3, learning_rate=0.05,
        subsample=0.8, random_state=42
    )
    clf.fit(X_scaled, y_dir)

    reg = GradientBoostingRegressor(
        n_estimators=100, max_depth=3, learning_rate=0.05,
        subsample=0.8, random_state=42
    )
    reg.fit(X_scaled, y_ret)

    joblib.dump(clf,    CLF_PATH)
    joblib.dump(reg,    REG_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump({'clf': clf, 'reg': reg, 'scaler': scaler, 'feat_cols': FEAT_COLS}, MODEL_PATH)

    return {
        "status": "success",
        "message": "Crypto model trained — honest walk-forward validation",
        "what_it_predicts": "Next trading day: price direction (UP/DOWN) + expected % change",
        "features_used": FEAT_COLS,
        "metrics": {
            "cv_direction_accuracy":     round(float(np.mean(dir_scores)), 4),
            "cv_direction_accuracy_std": round(float(np.std(dir_scores)),  4),
            "cv_return_mae_pct":         round(float(np.mean(ret_maes)) * 100, 4),
            "cv_folds":                  5,
            "training_samples":          int(len(X)),
            "symbols_used":              symbols or ["BTC"],
            "note": (
                "Direction accuracy ~51-54% is EXPECTED for crypto. "
                "Old model showed R²≈0.99 due to data leakage (same-candle High/Low). "
                "This version only uses information available before the next day opens."
            )
        }
    }


def predict_crypto(open_price: float = None, high_price: float = None,
                   low_price: float = None, recent_closes: list = None) -> dict:
    """
    Predict next day crypto price direction and expected % move.

    Parameters
    ----------
    recent_closes : list of float
        Last 35+ daily closing prices (required).
    open_price, high_price, low_price : float
        Today's intraday values (optional, improve hl_range feature).
    """
    if not os.path.exists(CLF_PATH):
        if not os.path.exists(MODEL_PATH):
            return {"error": "Crypto model not trained yet. Call /ml/crypto/train first."}
        bundle = joblib.load(MODEL_PATH)
        clf, reg, scaler = bundle['clf'], bundle['reg'], bundle['scaler']
    else:
        clf    = joblib.load(CLF_PATH)
        reg    = joblib.load(REG_PATH)
        scaler = joblib.load(SCALER_PATH)

    if recent_closes is None or len(recent_closes) < 35:
        return {
            "error": "Need at least 35 recent daily closing prices.",
            "hint":  "Pass recent_closes=[...] with 35+ values."
        }

    closes = pd.Series(recent_closes, dtype=float)
    dummy_df = pd.DataFrame({
        'Close':  closes,
        'High':   closes * 1.02 if high_price is None else ([closes.iloc[-1]] * (len(closes) - 1) + [high_price]),
        'Low':    closes * 0.98 if low_price  is None else ([closes.iloc[-1]] * (len(closes) - 1) + [low_price]),
        'Volume': [1e8] * len(closes)
    })
    feat = _engineer_features(dummy_df)
    if feat.empty:
        return {"error": "Not enough data after feature engineering."}

    X_last = scaler.transform(feat[FEAT_COLS].iloc[[-1]])

    direction     = int(clf.predict(X_last)[0])
    proba         = clf.predict_proba(X_last)[0]
    expected_move = float(reg.predict(X_last)[0])

    return {
        "prediction": {
            "direction":         "UP ▲" if direction == 1 else "DOWN ▼",
            "confidence_pct":    round(float(max(proba)) * 100, 1),
            "expected_move_pct": round(expected_move * 100, 2),
        },
        "disclaimer": (
            "Crypto prediction accuracy is ~51-54%. Use as one signal, not sole decision basis."
        )
    }


def is_model_trained() -> bool:
    return os.path.exists(MODEL_PATH) or os.path.exists(CLF_PATH)
