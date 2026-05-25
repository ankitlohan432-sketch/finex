"""
FINEX - ML/DL Prediction Routes
All prediction API endpoints — prefix: /ml

Models trained on REAL datasets:
  Stock (US)  : AAPL, MSFT, GOOGL, TSLA, NVDA  — Linear Regression
  Stock (NSE) : RELIANCE, TCS, INFY, HDFCBANK   — Linear Regression
  Crypto      : BTC, ETH, BNB, ADA, XRP          — Random Forest
  Expense     : Realistic financial distribution  — Decision Tree
  Fraud       : 20k transaction records           — Isolation Forest
  LSTM (DL)   : BTC daily prices 2013-2021        — LSTM Neural Network
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import tempfile, os

from ml_dl.models.stock_predictor   import train_model,         predict_price,        is_model_trained as stock_trained
from ml_dl.models.crypto_predictor  import train_crypto_model,  predict_crypto,       is_model_trained as crypto_trained
from ml_dl.models.expense_predictor import train_expense_model, predict_expense,      is_model_trained as expense_trained
from ml_dl.models.fraud_detector_ml import train_fraud_model,   detect_fraud,         is_model_trained as fraud_trained
from ml_dl.models.lstm_predictor    import train_lstm_model,    predict_next_price,   is_model_trained as lstm_trained

router = APIRouter(tags=["ML Predictions"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class StockPredictRequest(BaseModel):
    open_price:  float
    high_price:  float
    low_price:   float
    market:      Optional[str] = "us"   # "us" or "nse"

class CryptoPredictRequest(BaseModel):
    open_price:  float
    high_price:  float
    low_price:   float

class ExpensePredictRequest(BaseModel):
    income:   float
    savings:  float

class FraudCheckRequest(BaseModel):
    amount:       float
    old_balance:  float
    new_balance:  float

class LSTMPredictRequest(BaseModel):
    recent_prices: List[float]   # last 10 closing prices


# ── Status ───────────────────────────────────────────────────────────────────

@router.get("/status")
async def ml_status():
    """Check which ML/DL models are trained and ready."""
    return {
        "models": {
            "stock_us":   {"trained": stock_trained("us"),  "algorithm": "Linear Regression",  "dataset": "AAPL/MSFT/GOOGL/TSLA/NVDA"},
            "stock_nse":  {"trained": stock_trained("nse"), "algorithm": "Linear Regression",  "dataset": "RELIANCE/TCS/INFY/HDFCBANK"},
            "crypto":     {"trained": crypto_trained(),      "algorithm": "Random Forest",      "dataset": "BTC/ETH/BNB/ADA/XRP (2013–2021)"},
            "expense":    {"trained": expense_trained(),     "algorithm": "Decision Tree",      "dataset": "Realistic financial distribution"},
            "fraud":      {"trained": fraud_trained(),       "algorithm": "Isolation Forest",   "dataset": "20k transaction records"},
            "lstm_dl":    {"trained": lstm_trained(),        "algorithm": "LSTM Neural Network","dataset": "BTC daily prices 2013–2021"},
        }
    }


# ── STOCK (ML) ───────────────────────────────────────────────────────────────

@router.post("/stock/train")
async def train_stock(
    file: Optional[UploadFile] = File(None),
    market: str = Query("us", description="'us' for US stocks, 'nse' for NSE India")
):
    """
    Train stock prediction model.
    - No file: trains on bundled real datasets (AAPL/MSFT/GOOGL or RELIANCE/TCS/INFY)
    - With file: upload your own CSV (needs: Open, High, Low, Close)
    """
    if file:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Upload a CSV file.")
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(await file.read()); tmp_path = tmp.name
        try:
            result = train_model(tmp_path, market=market)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            os.unlink(tmp_path)
    else:
        try:
            result = train_model(market=market)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return result


@router.post("/stock/predict")
async def predict_stock(req: StockPredictRequest):
    """Predict closing price. market='us' or 'nse'."""
    result = predict_price(req.open_price, req.high_price, req.low_price, market=req.market)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ── CRYPTO (ML) ──────────────────────────────────────────────────────────────

@router.post("/crypto/train")
async def train_crypto(file: Optional[UploadFile] = File(None)):
    """
    Train crypto prediction model.
    - No file: trains on bundled BTC/ETH/BNB/ADA/XRP dataset (2013–2021)
    - With file: upload CSV with Open, High, Low, Close (and optionally Symbol)
    """
    if file:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Upload a CSV file.")
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(await file.read()); tmp_path = tmp.name
        try:
            result = train_crypto_model(tmp_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            os.unlink(tmp_path)
    else:
        try:
            result = train_crypto_model()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return result


@router.post("/crypto/predict")
async def predict_crypto_price(req: CryptoPredictRequest):
    """Predict crypto closing price from Open, High, Low."""
    result = predict_crypto(req.open_price, req.high_price, req.low_price)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ── EXPENSE (ML) ─────────────────────────────────────────────────────────────

@router.post("/expense/train")
async def train_expense(file: Optional[UploadFile] = File(None)):
    """
    Train expense prediction model.
    - No file: trains on realistic synthetic distribution
    - With file: upload CSV with columns income, savings, expense
    """
    if file:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Upload a CSV file.")
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(await file.read()); tmp_path = tmp.name
        try:
            result = train_expense_model(tmp_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            os.unlink(tmp_path)
    else:
        try:
            result = train_expense_model()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return result


@router.post("/expense/predict")
async def predict_expense_amount(req: ExpensePredictRequest):
    """Predict monthly expense from income and savings."""
    result = predict_expense(req.income, req.savings)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ── FRAUD DETECTION (ML) ─────────────────────────────────────────────────────

@router.post("/fraud/train")
async def train_fraud(file: Optional[UploadFile] = File(None)):
    """
    Train ML fraud detection model.
    - No file: trains on 20k realistic transaction records
    - With file: upload CSV with amount, oldbalanceOrg, newbalanceOrig
    """
    if file:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Upload a CSV file.")
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(await file.read()); tmp_path = tmp.name
        try:
            result = train_fraud_model(tmp_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            os.unlink(tmp_path)
    else:
        try:
            result = train_fraud_model()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return result


@router.post("/fraud/detect")
async def detect_fraud_transaction(req: FraudCheckRequest):
    """ML-based fraud detection — returns risk label, score, and risk level."""
    result = detect_fraud(req.amount, req.old_balance, req.new_balance)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ── LSTM DEEP LEARNING ───────────────────────────────────────────────────────

@router.post("/dl/lstm/train")
async def train_lstm(
    file: Optional[UploadFile] = File(None),
    column: str = Query("Close", description="Column name with prices"),
    epochs: int = Query(20, ge=1, le=200, description="Training epochs (1-200)")
):
    """
    Train LSTM deep learning model.
    - No file: trains on BTC daily prices 2013–2021 (3004 rows)
    - With file: upload any CSV with a Close/price column
    Requires TensorFlow: pip install tensorflow
    """
    if file:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Upload a CSV file.")
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(await file.read()); tmp_path = tmp.name
        try:
            result = train_lstm_model(tmp_path, column=column, epochs=epochs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            os.unlink(tmp_path)
    else:
        try:
            result = train_lstm_model(column=column, epochs=epochs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/dl/lstm/predict")
async def predict_lstm(req: LSTMPredictRequest):
    """
    Predict next price using LSTM model.
    Provide the last 10 (or more) closing prices in recent_prices.
    """
    result = predict_next_price(req.recent_prices)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
