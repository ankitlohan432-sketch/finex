# FINEX — ML/DL Prediction Module

Separate, self-contained module at `backend/ml_dl/`.
Only 2 lines were added to `main.py`. Nothing else in Finex was changed.

---

## 📁 Folder Structure

```
backend/ml_dl/
├── models/
│   ├── stock_predictor.py       Linear Regression  — US & NSE stocks
│   ├── crypto_predictor.py      Random Forest      — BTC/ETH/BNB/ADA/XRP
│   ├── expense_predictor.py     Decision Tree      — income/savings → expense
│   ├── fraud_detector_ml.py     Isolation Forest   — anomaly detection
│   ├── lstm_predictor.py        LSTM Neural Net    — next price (DL)
│   └── saved_models/            ← .pkl & .keras files saved here after training
├── routes/
│   └── ml_routes.py             All FastAPI /ml endpoints
├── datasets/
│   ├── stocks_us/               AAPL, MSFT, GOOGL, TSLA, NVDA, JPM, AMZN...
│   ├── stocks_nse/              RELIANCE, TCS, INFY, HDFCBANK, WIPRO, SBIN...
│   └── crypto/
│       ├── crypto_prices.csv    BTC/ETH/BNB/ADA/XRP 2013–2021 (2.1M rows)
│       ├── crypto-markets.csv   942k rows multi-coin history
│       └── btc_daily.csv        BTC daily close prices (LSTM training data)
└── README.md
```

---

## 🤖 Models & Real Datasets Used

| Model | Algorithm | Dataset | Samples |
|---|---|---|---|
| Stock US | Linear Regression | AAPL+MSFT+GOOGL+TSLA+NVDA | 26,270 |
| Stock NSE | Linear Regression | RELIANCE+TCS+INFY+HDFCBANK+WIPRO | 145,573 |
| Crypto | Random Forest | BTC+ETH+BNB+ADA+XRP (2013–2021) | 10,926 |
| Expense | Decision Tree | Realistic synthetic distribution | 5,000 |
| Fraud | Isolation Forest | 20,000 transaction records | 20,000 |
| LSTM (DL) | LSTM Neural Network | BTC daily close prices | 3,004 |

---

## 🌐 API Endpoints  (all under `/ml`)

```
GET  /ml/status              → Which models are trained

POST /ml/stock/train         → Train stock model (no file = uses bundled datasets)
POST /ml/stock/predict       → {"open_price":150, "high_price":155, "low_price":148, "market":"us"}

POST /ml/crypto/train        → Train crypto model (no file = uses bundled dataset)
POST /ml/crypto/predict      → {"open_price":45000, "high_price":46000, "low_price":44000}

POST /ml/expense/train       → Train expense model
POST /ml/expense/predict     → {"income":80000, "savings":10000}

POST /ml/fraud/train         → Train fraud model
POST /ml/fraud/detect        → {"amount":500, "old_balance":5000, "new_balance":4500}

POST /ml/dl/lstm/train       → Train LSTM (add ?epochs=20) — needs tensorflow
POST /ml/dl/lstm/predict     → {"recent_prices":[34000,35000,...]}  (last 10 prices)
```

---

## ⚙️ Install & Run

```bash
# 1. Install ML dependencies
pip install scikit-learn joblib numpy pandas

# 2. Install DL (only for LSTM endpoints)
pip install tensorflow

# 3. Start backend
cd backend
uvicorn main:app --reload

# 4. Open Swagger UI
# http://localhost:8000/docs  →  "ML Predictions" section
```

---

## 🧪 Quick Test (no dataset upload needed!)

All models train automatically from bundled datasets:

```bash
# Train all models at once
curl -X POST http://localhost:8000/ml/stock/train?market=us
curl -X POST http://localhost:8000/ml/stock/train?market=nse
curl -X POST http://localhost:8000/ml/crypto/train
curl -X POST http://localhost:8000/ml/expense/train
curl -X POST http://localhost:8000/ml/fraud/train

# Make predictions
curl -X POST http://localhost:8000/ml/stock/predict \
  -H "Content-Type: application/json" \
  -d '{"open_price":150,"high_price":155,"low_price":148,"market":"us"}'

curl -X POST http://localhost:8000/ml/fraud/detect \
  -H "Content-Type: application/json" \
  -d '{"amount":49000,"old_balance":49500,"new_balance":0}'
```

---

## 🧠 DL Concept — LSTM Architecture

```
Input: 10 past closing prices
         ↓
   LSTM Layer (64 units)     learns long-term price patterns
         ↓
   Dropout (20%)             prevents overfitting
         ↓
   LSTM Layer (32 units)     refines the patterns
         ↓
   Dropout (20%)
         ↓
   Dense Layer (16 units)    extracts key features
         ↓
   Dense Layer (1 unit)      outputs single predicted price
         ↓
  Predicted Next Close Price
```

Why LSTM? Stock/crypto prices are **time-series** data — each price depends
on past prices. LSTM is a special neural network that **remembers** past
information through its hidden state, making it ideal for price prediction.
