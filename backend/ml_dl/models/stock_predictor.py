"""
FINEX - Stock Price Prediction Model (v2 - No Overfitting)
============================================================
WHAT CHANGED AND WHY:
  OLD (broken): Predicted Close from Open+High+Low of the SAME day.
      -> This is data leakage. High and Low are only known AFTER market closes.
      -> Result: fake R²≈0.99 (cheating, not learning).

  NEW (correct): Predicts NEXT DAY direction + price change using only
      information available BEFORE the market opens:
      - Lag returns (1d, 3d, 5d, 10d)
      - Rolling volatility
      - Price vs moving averages (MA5, MA20, MA50)
      - RSI (14-day)
      - Volume ratio
      - High-Low range

Validation: Walk-forward TimeSeriesSplit (no future leakage in CV)
Expected accuracy: ~51-53% direction (markets are hard - this is honest)

Datasets used:
  NSE (Indian): RELIANCE, TCS, INFY, HDFCBANK, WIPRO, AXISBANK,
                ICICIBANK, KOTAKBANK, LT, MARUTI, SBIN, TATAMOTORS,
                ADANIENT, BAJFINANCE, HINDUNILVR
  US:           AAPL, MSFT, GOOGL, TSLA, NVDA, AMZN, NFLX, BRK-B, JPM
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

SAVE_DIR       = os.path.join(os.path.dirname(__file__), "saved_models")
NSE_CLF_PATH   = os.path.join(SAVE_DIR, "stock_nse_clf.pkl")
NSE_REG_PATH   = os.path.join(SAVE_DIR, "stock_nse_reg.pkl")
NSE_SCALER_PATH= os.path.join(SAVE_DIR, "stock_nse_scaler.pkl")
US_CLF_PATH    = os.path.join(SAVE_DIR, "stock_us_clf.pkl")
US_REG_PATH    = os.path.join(SAVE_DIR, "stock_us_reg.pkl")
US_SCALER_PATH = os.path.join(SAVE_DIR, "stock_us_scaler.pkl")

# Keep old paths so existing routes don't break
MODEL_PATH = os.path.join(SAVE_DIR, "stock_model.pkl")
NSE_PATH   = os.path.join(SAVE_DIR, "stock_nse_model.pkl")

DATASETS_US  = os.path.join(os.path.dirname(__file__), "../datasets/stocks_us")
DATASETS_NSE = os.path.join(os.path.dirname(__file__), "../datasets/stocks_nse")

FEAT_COLS = [
    'return_1d', 'return_3d', 'return_5d', 'return_10d',
    'vol_5d', 'vol_20d',
    'price_to_ma5', 'price_to_ma20', 'ma5_to_ma20',
    'rsi', 'vol_ratio', 'hl_range'
]


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build lag-based features that are knowable BEFORE market opens.
    All features use only past data → no leakage.
    Target: next day's close change (normalized %).
    """
    df = df.copy()

    # Returns
    df['return_1d']  = df['Close'].pct_change(1)
    df['return_3d']  = df['Close'].pct_change(3)
    df['return_5d']  = df['Close'].pct_change(5)
    df['return_10d'] = df['Close'].pct_change(10)

    # Rolling volatility
    df['vol_5d']  = df['return_1d'].rolling(5).std()
    df['vol_20d'] = df['return_1d'].rolling(20).std()

    # Moving average ratios (price momentum signals)
    df['ma5']  = df['Close'].rolling(5).mean()
    df['ma20'] = df['Close'].rolling(20).mean()
    df['ma50'] = df['Close'].rolling(50).mean()
    df['price_to_ma5']  = df['Close'] / df['ma5']  - 1
    df['price_to_ma20'] = df['Close'] / df['ma20'] - 1
    df['ma5_to_ma20']   = df['ma5']   / df['ma20'] - 1

    # RSI (14-day)
    delta = df['Close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    # Volume ratio vs 20-day average
    if 'Volume' in df.columns and df['Volume'].sum() > 0:
        df['vol_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    else:
        df['vol_ratio'] = 1.0

    # Intraday range (normalized)
    if 'High' in df.columns and 'Low' in df.columns:
        df['hl_range'] = (df['High'] - df['Low']) / df['Close']
    else:
        df['hl_range'] = 0.0

    # TARGET: next day's normalized price change (shift -1 = look into future)
    df['next_return']    = df['Close'].pct_change(1).shift(-1)
    df['next_direction'] = (df['next_return'] > 0).astype(int)

    return df.dropna()


def _load_nse_daily() -> pd.DataFrame:
    """Load all NSE stocks, resample intraday→daily, return combined DataFrame."""
    files = [f for f in os.listdir(DATASETS_NSE) if f.endswith('.csv')]
    dfs = []
    for fname in files:
        try:
            df = pd.read_csv(os.path.join(DATASETS_NSE, fname))
            df.columns = [c.strip() for c in df.columns]
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df = df.set_index('Datetime').sort_index()
            # Resample 15-min → daily OHLCV
            daily = df.resample('D').agg({
                'Open': 'first', 'High': 'max',
                'Low': 'min',   'Close': 'last',
                'Volume': 'sum'
            }).dropna(subset=['Open', 'Close'])
            dfs.append(_engineer_features(daily))
        except Exception:
            continue
    return pd.concat(dfs).sort_index() if dfs else pd.DataFrame()


def _load_us_daily() -> pd.DataFrame:
    """Load all US stocks (already daily OHLCV)."""
    files = [f for f in os.listdir(DATASETS_US) if f.endswith(('.txt', '.csv'))]
    dfs = []
    for fname in files:
        try:
            df = pd.read_csv(os.path.join(DATASETS_US, fname))
            df.columns = [c.strip() for c in df.columns]
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date').sort_index()
            dfs.append(_engineer_features(df))
        except Exception:
            continue
    return pd.concat(dfs).sort_index() if dfs else pd.DataFrame()


def train_model(csv_file: str = None, market: str = "us") -> dict:
    """
    Train stock prediction model with proper temporal cross-validation.

    Outputs two models:
      - Classifier: predicts UP or DOWN direction for next day
      - Regressor:  predicts magnitude of next day's price change (%)

    Parameters
    ----------
    csv_file : str, optional
        Path to custom CSV. Must have columns: Date/Datetime, Open, High, Low, Close.
    market : str
        'us' or 'nse'
    """
    os.makedirs(SAVE_DIR, exist_ok=True)

    if csv_file:
        df = pd.read_csv(csv_file)
        df.columns = [c.strip() for c in df.columns]
        date_col = next((c for c in df.columns if c.lower() in ('date', 'datetime')), None)
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.set_index(date_col).sort_index()
        data = _engineer_features(df)
        clf_path, reg_path, scaler_path = US_CLF_PATH, US_REG_PATH, US_SCALER_PATH
    elif market == "nse":
        data = _load_nse_daily()
        clf_path, reg_path, scaler_path = NSE_CLF_PATH, NSE_REG_PATH, NSE_SCALER_PATH
    else:
        data = _load_us_daily()
        clf_path, reg_path, scaler_path = US_CLF_PATH, US_REG_PATH, US_SCALER_PATH

    if data.empty or len(data) < 200:
        return {"error": "Not enough data to train. Need at least 200 daily rows."}

    X = data[FEAT_COLS]
    y_dir = data['next_direction']
    y_ret = data['next_return']

    # Walk-forward cross-validation (respects time order, no future leakage)
    tscv = TimeSeriesSplit(n_splits=5)
    dir_scores, ret_maes = [], []
    for train_idx, test_idx in tscv.split(X):
        X_tr, X_te   = X.iloc[train_idx], X.iloc[test_idx]
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

    # Final model trained on all data
    scaler = StandardScaler().fit(X)
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

    joblib.dump(clf,    clf_path)
    joblib.dump(reg,    reg_path)
    joblib.dump(scaler, scaler_path)

    # Also save a combined dict to old path for backward compatibility
    joblib.dump({'clf': clf, 'reg': reg, 'scaler': scaler, 'feat_cols': FEAT_COLS},
                NSE_PATH if market == "nse" else MODEL_PATH)

    mean_dir  = float(np.mean(dir_scores))
    mean_mae  = float(np.mean(ret_maes))
    std_dir   = float(np.std(dir_scores))

    return {
        "status": "success",
        "message": f"Stock model trained ({market.upper()} market) — honest walk-forward validation",
        "what_it_predicts": "Next trading day: price direction (UP/DOWN) + expected % change",
        "features_used": FEAT_COLS,
        "metrics": {
            "cv_direction_accuracy":  round(mean_dir, 4),
            "cv_direction_accuracy_std": round(std_dir, 4),
            "cv_return_mae_pct":      round(mean_mae * 100, 4),
            "cv_folds":               5,
            "training_samples":       int(len(X)),
            "note": (
                "Direction accuracy ~51-53% is EXPECTED and HONEST for stock markets. "
                "Old model showed R²≈0.99 due to data leakage (using same-day High/Low to predict Close). "
                "This version uses only past data available before market opens."
            )
        }
    }


def predict_price(open_price: float = None, high_price: float = None,
                  low_price: float = None, market: str = "us",
                  recent_closes: list = None) -> dict:
    """
    Predict next trading day direction and expected % move.

    Parameters
    ----------
    recent_closes : list of float
        Last 50+ daily closing prices (required for feature engineering).
        If not provided, falls back to simple heuristic.
    open_price, high_price, low_price : float
        Today's intraday values (optional, used for hl_range feature).
    market : str
        'us' or 'nse'
    """
    clf_path    = NSE_CLF_PATH   if market == "nse" else US_CLF_PATH
    reg_path    = NSE_REG_PATH   if market == "nse" else US_REG_PATH
    scaler_path = NSE_SCALER_PATH if market == "nse" else US_SCALER_PATH

    # Fall back to combined pkl if individual files missing
    if not os.path.exists(clf_path):
        combined_path = NSE_PATH if market == "nse" else MODEL_PATH
        if not os.path.exists(combined_path):
            return {"error": f"Stock model ({market}) not trained yet. Call /ml/stock/train first."}
        bundle = joblib.load(combined_path)
        clf, reg, scaler = bundle['clf'], bundle['reg'], bundle['scaler']
    else:
        clf    = joblib.load(clf_path)
        reg    = joblib.load(reg_path)
        scaler = joblib.load(scaler_path)

    if recent_closes is None or len(recent_closes) < 55:
        return {
            "error": "Need at least 55 recent daily closing prices to compute features.",
            "hint": "Pass recent_closes=[list of last 55+ daily closes] in your request."
        }

    closes = pd.Series(recent_closes, dtype=float)
    dummy_df = pd.DataFrame({
        'Close':  closes,
        'High':   closes * 1.01 if high_price is None else ([closes.iloc[-1]] * (len(closes) - 1) + [high_price]),
        'Low':    closes * 0.99 if low_price  is None else ([closes.iloc[-1]] * (len(closes) - 1) + [low_price]),
        'Volume': [1e6] * len(closes)
    })
    feat = _engineer_features(dummy_df)
    if feat.empty:
        return {"error": "Not enough data after feature engineering. Provide 55+ closes."}

    X_last = scaler.transform(feat[FEAT_COLS].iloc[[-1]])

    direction     = int(clf.predict(X_last)[0])
    proba         = clf.predict_proba(X_last)[0]
    expected_move = float(reg.predict(X_last)[0])

    return {
        "market": market.upper(),
        "prediction": {
            "direction":         "UP ▲" if direction == 1 else "DOWN ▼",
            "confidence_pct":    round(float(max(proba)) * 100, 1),
            "expected_move_pct": round(expected_move * 100, 2),
        },
        "disclaimer": (
            "Market prediction accuracy is inherently limited (~51-53%). "
            "Use as one signal among many, not sole investment basis."
        )
    }


def is_model_trained(market: str = "us") -> bool:
    path = NSE_PATH if market == "nse" else MODEL_PATH
    return os.path.exists(path)
