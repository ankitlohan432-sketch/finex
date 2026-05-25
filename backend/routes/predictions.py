"""
FINEX - AI Predictions Route
Uses Binance klines for crypto (reliable)
Uses yfinance headers trick for NSE/BSE
"""
from fastapi import APIRouter, Query
from services.crypto_market_service import get_crypto_ticker, get_crypto_klines
from services.india_market_service import get_nse_quote, get_bse_quote, get_nse_klines, get_bse_klines
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["AI Predictions"])

def simple_ml_predict(prices: list) -> dict:
    if len(prices) < 5:
        return {"signal": "NEUTRAL", "confidence": 0, "reason": "Insufficient data"}

    arr = np.array(prices, dtype=float)

    # Moving Averages
    ma5  = np.mean(arr[-5:])
    ma10 = np.mean(arr[-10:])
    ma20 = np.mean(arr[-20:])
    current = arr[-1]

    # RSI
    deltas = np.diff(arr[-15:])
    gains  = deltas[deltas > 0]
    losses = abs(deltas[deltas < 0])
    avg_gain = np.mean(gains)  if len(gains)  > 0 else 0
    avg_loss = np.mean(losses) if len(losses) > 0 else 0.0001
    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # MACD
    ema12 = np.mean(arr[-12:])
    ema26 = np.mean(arr[-26:]) if len(arr) >= 26 else np.mean(arr)
    macd  = ema12 - ema26

    # Momentum
    momentum = (current - arr[-6]) / arr[-6] * 100 if arr[-6] != 0 else 0

    score = 0
    reasons = []

    if ma5 > ma10 > ma20:
        score += 2
        reasons.append("Bullish MA alignment")
    elif ma5 < ma10 < ma20:
        score -= 2
        reasons.append("Bearish MA alignment")

    if rsi < 30:
        score += 2
        reasons.append(f"Oversold RSI ({rsi:.0f})")
    elif rsi > 70:
        score -= 2
        reasons.append(f"Overbought RSI ({rsi:.0f})")
    elif 40 < rsi < 60:
        score += 1
        reasons.append(f"Neutral RSI ({rsi:.0f})")

    if macd > 0:
        score += 1
        reasons.append("Positive MACD")
    else:
        score -= 1
        reasons.append("Negative MACD")

    if momentum > 1:
        score += 1
        reasons.append(f"Strong momentum +{momentum:.1f}%")
    elif momentum < -1:
        score -= 1
        reasons.append(f"Weak momentum {momentum:.1f}%")

    if current > ma20 * 1.02:
        score += 1
    elif current < ma20 * 0.98:
        score -= 1

    confidence = min(abs(score) / 7 * 100, 95)

    if score >= 3:
        signal = "STRONG BUY"
        color  = "#00e5a0"
    elif score >= 1:
        signal = "BUY"
        color  = "#4ade80"
    elif score <= -3:
        signal = "STRONG SELL"
        color  = "#ff4444"
    elif score <= -1:
        signal = "SELL"
        color  = "#f87171"
    else:
        signal = "NEUTRAL"
        color  = "#fbbf24"
        confidence = max(confidence, 40)

    if len(arr) >= 5:
        recent = arr[-5:]
        x = np.arange(5)
        slope = np.polyfit(x, recent, 1)[0]
        predicted_price = current + slope
    else:
        predicted_price = current

    change_pct = ((predicted_price - current) / current * 100) if current != 0 else 0

    return {
        "signal":          signal,
        "color":           color,
        "confidence":      round(confidence, 1),
        "predicted_price": round(float(predicted_price), 6),
        "change_pct":      round(float(change_pct), 2),
        "rsi":             round(float(rsi), 1),
        "macd":            round(float(macd), 6),
        "ma5":             round(float(ma5), 6),
        "ma10":            round(float(ma10), 6),
        "ma20":            round(float(ma20), 6),
        "momentum":        round(float(momentum), 2),
        "reasons":         reasons[:3],
        "timestamp":       datetime.utcnow().isoformat(),
    }


@router.get("/crypto/{symbol}")
async def predict_crypto(
    symbol: str,
    interval: str = Query("1h", regex="^(5m|15m|1h|4h|1d)$")
):
    try:
        candles = await get_crypto_klines(symbol.upper(), interval=interval, limit=60)
        if not candles or len(candles) < 5:
            return {"error": "Insufficient market data", "signal": "NEUTRAL", "confidence": 0}

        prices = [c["close"] for c in candles]
        current_ticker = await get_crypto_ticker(symbol.upper())
        current_price  = current_ticker["price"] if current_ticker else prices[-1]

        prediction = simple_ml_predict(prices)
        prediction["current_price"] = round(float(current_price), 6)
        prediction["symbol"]        = symbol.upper()
        prediction["market"]        = "crypto"
        prediction["interval"]      = interval
        prediction["data_points"]   = len(prices)
        return prediction
    except Exception as e:
        logger.error(f"Crypto prediction error {symbol}: {e}")
        return {"error": str(e), "signal": "NEUTRAL", "confidence": 0}


@router.get("/nse/{symbol}")
async def predict_nse(
    symbol: str,
    interval: str = Query("1d", regex="^(1h|1d|1wk)$")
):
    try:
        candles = await get_nse_klines(symbol.upper(), interval=interval)
        if not candles or len(candles) < 5:
            return {"error": "Insufficient data", "signal": "NEUTRAL", "confidence": 0}

        prices = [c["close"] for c in candles]
        ticker = await get_nse_quote(symbol.upper())
        current_price = ticker["price"] if ticker else prices[-1]

        prediction = simple_ml_predict(prices)
        prediction["current_price"] = round(float(current_price), 2)
        prediction["symbol"]        = symbol.upper()
        prediction["market"]        = "nse"
        prediction["interval"]      = interval
        return prediction
    except Exception as e:
        logger.error(f"NSE prediction error {symbol}: {e}")
        return {"error": str(e), "signal": "NEUTRAL", "confidence": 0}


@router.get("/bse/{symbol}")
async def predict_bse(
    symbol: str,
    interval: str = Query("1d", regex="^(1h|1d|1wk)$")
):
    try:
        candles = await get_bse_klines(symbol.upper(), interval=interval)
        if not candles or len(candles) < 5:
            return {"error": "Insufficient data", "signal": "NEUTRAL", "confidence": 0}

        prices = [c["close"] for c in candles]
        ticker = await get_bse_quote(symbol.upper())
        current_price = ticker["price"] if ticker else prices[-1]

        prediction = simple_ml_predict(prices)
        prediction["current_price"] = round(float(current_price), 2)
        prediction["symbol"]        = symbol.upper()
        prediction["market"]        = "bse"
        prediction["interval"]      = interval
        return prediction
    except Exception as e:
        logger.error(f"BSE prediction error {symbol}: {e}")
        return {"error": str(e), "signal": "NEUTRAL", "confidence": 0}


