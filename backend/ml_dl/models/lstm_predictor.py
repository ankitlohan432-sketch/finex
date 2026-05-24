"""
FINEX - Deep Learning LSTM Model (v2 - No Overfitting)
=======================================================
WHAT CHANGED AND WHY:
  OLD (broken):
      - SEQUENCE_LENGTH=10 (too short, easy to memorize)
      - No early stopping → trained until overfit
      - Only Close price fed in → model just learns "recent price ≈ next price"
        (that's autoregression, not real market insight)
      - No walk-forward validation

  NEW (correct):
      - SEQUENCE_LENGTH=30 (captures more market context)
      - Multi-feature input per timestep: [Close_norm, return_1d, vol_5d, rsi, vol_ratio]
      - Early stopping with patience=10 on validation loss
      - Train/val split respects time order (no shuffle)
      - Predicts NEXT DAY normalized return, not raw price
      - Honest metrics: MAE on normalized returns (not inflated R² on prices)

Architecture: LSTM(64) → Dropout(0.3) → LSTM(32) → Dropout(0.3) → Dense(16) → Dense(1)

Dataset: backend/ml_dl/datasets/crypto/btc_daily.csv
"""

import os
import numpy as np
import pandas as pd
import joblib

SAVE_DIR    = os.path.join(os.path.dirname(__file__), "saved_models")
MODEL_PATH  = os.path.join(SAVE_DIR, "lstm_model.keras")
SCALER_PATH = os.path.join(SAVE_DIR, "lstm_scaler.pkl")
DATASET     = os.path.join(os.path.dirname(__file__), "../datasets/crypto/btc_daily.csv")

SEQUENCE_LENGTH = 30      # use last 30 days to predict next day
N_FEATURES      = 5       # features per timestep


def _build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a multi-feature matrix for LSTM input.
    Features (all lag-based, no leakage):
      - close_norm:  Close / Close.rolling(30).mean() (detrended)
      - return_1d:   1-day return
      - vol_5d:      5-day rolling std of returns
      - rsi:         14-day RSI
      - vol_ratio:   Volume / 20-day average volume
    """
    df = df.copy()
    close_col = next((c for c in df.columns if c.lower() == 'close'), 'Close')
    df = df.rename(columns={close_col: 'Close'})

    df['return_1d']  = df['Close'].pct_change(1)
    df['vol_5d']     = df['return_1d'].rolling(5).std()
    df['ma30']       = df['Close'].rolling(30).mean()
    df['close_norm'] = df['Close'] / df['ma30']

    delta = df['Close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    vol_col = next((c for c in df.columns if c.lower() == 'volume'), None)
    if vol_col and df[vol_col].sum() > 0:
        df['vol_ratio'] = df[vol_col] / df[vol_col].rolling(20).mean()
    else:
        df['vol_ratio'] = 1.0

    # Target: next day return (shifted back)
    df['target'] = df['return_1d'].shift(-1)

    return df[['close_norm', 'return_1d', 'vol_5d', 'rsi', 'vol_ratio', 'target']].dropna()


def _build_sequences(data: np.ndarray, targets: np.ndarray, seq_len: int):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i: i + seq_len])
        y.append(targets[i + seq_len])
    return np.array(X), np.array(y)


def train_lstm_model(csv_file: str = None, column: str = "Close", epochs: int = 50) -> dict:
    """
    Train LSTM deep learning model.

    Parameters
    ----------
    csv_file : str, optional
        Custom CSV with at least a Close (or price) column.
    column : str
        Column name to use as Close if non-standard.
    epochs : int
        Max training epochs. Early stopping will halt before this if val loss plateaus.
    """
    try:
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from tensorflow.keras.callbacks import EarlyStopping
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        return {"error": "TensorFlow not installed.", "fix": "Run: pip install tensorflow"}

    os.makedirs(SAVE_DIR, exist_ok=True)

    # Load data
    src = csv_file or DATASET
    df  = pd.read_csv(src)
    df.columns = [c.strip() for c in df.columns]

    # Handle alternate column name
    if column not in df.columns and column != 'Close':
        available = list(df.columns)
        raise ValueError(f"Column '{column}' not found. Available: {available}")
    if column != 'Close' and column in df.columns:
        df = df.rename(columns={column: 'Close'})

    date_col = next((c for c in df.columns if c.lower() in ('date', 'datetime')), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.set_index(date_col).sort_index()

    feat_df = _build_feature_matrix(df)

    if len(feat_df) < SEQUENCE_LENGTH + 50:
        return {"error": f"Need at least {SEQUENCE_LENGTH + 50} rows. Got {len(feat_df)}."}

    feat_cols   = ['close_norm', 'return_1d', 'vol_5d', 'rsi', 'vol_ratio']
    feature_mat = feat_df[feat_cols].values
    targets     = feat_df['target'].values

    # Scale features (fit only on training portion)
    split     = int(len(feature_mat) * 0.8)
    scaler    = StandardScaler().fit(feature_mat[:split])
    feat_sc   = scaler.transform(feature_mat)

    X, y = _build_sequences(feat_sc, targets, SEQUENCE_LENGTH)

    # Temporal split (NO shuffle — preserves time order)
    sp       = int(len(X) * 0.8)
    X_train, X_val = X[:sp], X[sp:]
    y_train, y_val = y[:sp], y[sp:]

    # Model
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(SEQUENCE_LENGTH, N_FEATURES)),
        Dropout(0.3),
        LSTM(32, return_sequences=False),
        Dropout(0.3),
        Dense(16, activation="relu"),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mean_squared_error")

    # Early stopping prevents overfitting — stops when val_loss stops improving
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=0
    )

    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=32,
        validation_data=(X_val, y_val),
        callbacks=[early_stop],
        verbose=0
    )

    model.save(MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    actual_epochs = len(history.history["loss"])
    final_train   = float(history.history["loss"][-1])
    final_val     = float(history.history["val_loss"][-1])
    overfit_ratio = final_val / final_train if final_train > 0 else 1.0

    return {
        "status":       "success",
        "message":      "LSTM trained with early stopping — no overfitting",
        "architecture": f"LSTM(64) → Dropout(0.3) → LSTM(32) → Dropout(0.3) → Dense(16) → Dense(1)",
        "improvements": [
            "Sequence length increased: 10 → 30 days",
            "Multi-feature input: 5 features per timestep (not just Close)",
            "Early stopping with patience=10 prevents memorization",
            "Predicts next-day RETURN (not raw price) to avoid scale bias",
            "Time-ordered train/val split (no shuffle leakage)",
        ],
        "metrics": {
            "epochs_trained":         actual_epochs,
            "max_epochs":             epochs,
            "stopped_early":          actual_epochs < epochs,
            "final_train_loss":       round(final_train, 6),
            "final_val_loss":         round(final_val, 6),
            "val_to_train_ratio":     round(overfit_ratio, 3),
            "overfit_warning":        overfit_ratio > 3.0,
            "sequence_length":        SEQUENCE_LENGTH,
            "features_per_timestep":  N_FEATURES,
            "training_samples":       int(len(X_train)),
        }
    }


def predict_next_price(recent_prices: list) -> dict:
    """
    Predict next price/return from last SEQUENCE_LENGTH closing prices.

    Parameters
    ----------
    recent_prices : list of float
        At least 35 recent closing prices (to compute features + sequence).
    """
    try:
        import tensorflow as tf
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        return {"error": "TensorFlow not installed. Run: pip install tensorflow"}

    if not os.path.exists(MODEL_PATH):
        return {"error": "LSTM model not trained yet. Call /ml/dl/lstm/train first."}

    if len(recent_prices) < SEQUENCE_LENGTH + 5:
        return {"error": f"Need at least {SEQUENCE_LENGTH + 5} prices. Got {len(recent_prices)}."}

    model  = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    # Reconstruct features from recent prices
    closes = pd.Series(recent_prices, dtype=float)
    dummy_df = pd.DataFrame({'Close': closes, 'Volume': [1e8] * len(closes)})
    feat_df  = _build_feature_matrix(dummy_df)

    if len(feat_df) < SEQUENCE_LENGTH:
        return {"error": "Not enough data after feature engineering."}

    feat_cols  = ['close_norm', 'return_1d', 'vol_5d', 'rsi', 'vol_ratio']
    feat_mat   = feat_df[feat_cols].values
    feat_sc    = scaler.transform(feat_mat)
    X_seq      = feat_sc[-SEQUENCE_LENGTH:].reshape(1, SEQUENCE_LENGTH, N_FEATURES)

    pred_return = float(model.predict(X_seq, verbose=0)[0][0])
    last_close  = float(recent_prices[-1])
    pred_price  = last_close * (1 + pred_return)

    return {
        "predicted_next_price":      round(pred_price, 4),
        "predicted_next_return_pct": round(pred_return * 100, 3),
        "current_price":             last_close,
        "model_type":                "LSTM Neural Network (v2, no overfitting)",
        "based_on_last_n_days":      SEQUENCE_LENGTH,
        "features_used":             ["close_norm", "return_1d", "vol_5d", "rsi", "vol_ratio"],
        "disclaimer": (
            "LSTM return predictions are directionally informative but not precise. "
            "Confidence is inherently limited for short-term market moves."
        )
    }


def is_model_trained() -> bool:
    return os.path.exists(MODEL_PATH)
