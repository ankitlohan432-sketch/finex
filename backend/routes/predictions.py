"""
FINEX - Market Prediction Routes
ML/DL predictions for Crypto, NSE, BSE
GET predictions for any symbol with BUY/SELL signals
"""

from fastapi import APIRouter, Query
from services.ml_predictor import ml_predictor
from services.dl_predictor import dl_predictor
from services.market_data_collector import market_collector
from services.crypto_market_service import get_crypto_ticker
from services.india_market_service import get_nse_quote, get_bse_quote
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["AI Predictions"])

@router.get("/predict/ensemble/crypto/{symbol}")
async def ensemble_crypto_prediction(symbol: str):
    """ML + DL Ensemble prediction for crypto"""
    try:
        current = await get_crypto_ticker(symbol.upper())
        if not current:
            return {"error": "Symbol not found"}
        
        historical = market_collector.get_historical_data('crypto', symbol.upper(), hours=24)
        if not historical:
            return {"signal": "HOLD", "confidence": 0.0, "reason": "No historical data"}
        
        if symbol.upper() not in ml_predictor.trained_symbols:
            ml_predictor.train_model(symbol.upper(), 'crypto', historical)
        if symbol.upper() not in dl_predictor.trained_symbols:
            dl_predictor.train_lstm(symbol.upper(), historical)
            dl_predictor.train_gru(symbol.upper(), historical)
        
        ml_pred = ml_predictor.predict(symbol.upper(), current, historical)
        dl_pred = dl_predictor.ensemble_prediction(symbol.upper(), historical)
        
        ml_score = ml_pred.get('ml_score', 0.5)
        dl_score = dl_pred.get('dl_ensemble_score', 0.5)
        combined_score = (ml_score + dl_score) / 2
        
        if combined_score >= 0.55:
            final_signal = 'BUY'
            confidence = min(combined_score, 0.95)
        elif combined_score <= 0.45:
            final_signal = 'SELL'
            confidence = min(1 - combined_score, 0.95)
        else:
            final_signal = 'HOLD'
            confidence = 0.5
        
        return {
            "symbol": symbol.upper(),
            "market": "Crypto",
            "current_price": current.get('price'),
            "final_prediction": {
                "signal": final_signal,
                "confidence": round(confidence, 3),
                "combined_score": round(combined_score, 3)
            },
            "ml_prediction": ml_pred,
            "dl_prediction": dl_pred,
            "model_type": "Ensemble (ML + DL)"
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}

@router.get("/predict/ensemble/nse/{symbol}")
async def ensemble_nse_prediction(symbol: str):
    """ML + DL Ensemble prediction for NSE"""
    try:
        current = await get_nse_quote(symbol.upper())
        if not current:
            return {"error": "Symbol not found"}
        
        historical = market_collector.get_historical_data('nse', symbol.upper(), hours=24)
        if not historical:
            return {"signal": "HOLD", "confidence": 0.0}
        
        if symbol.upper() not in ml_predictor.trained_symbols:
            ml_predictor.train_model(symbol.upper(), 'nse', historical)
        if symbol.upper() not in dl_predictor.trained_symbols:
            dl_predictor.train_lstm(symbol.upper(), historical)
            dl_predictor.train_gru(symbol.upper(), historical)
        
        ml_pred = ml_predictor.predict(symbol.upper(), current, historical)
        dl_pred = dl_predictor.ensemble_prediction(symbol.upper(), historical)
        
        ml_score = ml_pred.get('ml_score', 0.5)
        dl_score = dl_pred.get('dl_ensemble_score', 0.5)
        combined_score = (ml_score + dl_score) / 2
        
        if combined_score >= 0.55:
            final_signal = 'BUY'
            confidence = min(combined_score, 0.95)
        elif combined_score <= 0.45:
            final_signal = 'SELL'
            confidence = min(1 - combined_score, 0.95)
        else:
            final_signal = 'HOLD'
            confidence = 0.5
        
        return {
            "symbol": symbol.upper(),
            "market": "NSE",
            "current_price": current.get('price'),
            "final_prediction": {
                "signal": final_signal,
                "confidence": round(confidence, 3)
            },
            "ml_prediction": ml_pred,
            "dl_prediction": dl_pred,
            "model_type": "Ensemble (ML + DL)"
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}

@router.get("/predict/ensemble/bse/{symbol}")
async def ensemble_bse_prediction(symbol: str):
    """ML + DL Ensemble prediction for BSE"""
    try:
        current = await get_bse_quote(symbol.upper())
        if not current:
            return {"error": "Symbol not found"}
        
        historical = market_collector.get_historical_data('bse', symbol.upper(), hours=24)
        if not historical:
            return {"signal": "HOLD", "confidence": 0.0}
        
        if symbol.upper() not in ml_predictor.trained_symbols:
            ml_predictor.train_model(symbol.upper(), 'bse', historical)
        if symbol.upper() not in dl_predictor.trained_symbols:
            dl_predictor.train_lstm(symbol.upper(), historical)
            dl_predictor.train_gru(symbol.upper(), historical)
        
        ml_pred = ml_predictor.predict(symbol.upper(), current, historical)
        dl_pred = dl_predictor.ensemble_prediction(symbol.upper(), historical)
        
        ml_score = ml_pred.get('ml_score', 0.5)
        dl_score = dl_pred.get('dl_ensemble_score', 0.5)
        combined_score = (ml_score + dl_score) / 2
        
        if combined_score >= 0.55:
            final_signal = 'BUY'
            confidence = min(combined_score, 0.95)
        elif combined_score <= 0.45:
            final_signal = 'SELL'
            confidence = min(1 - combined_score, 0.95)
        else:
            final_signal = 'HOLD'
            confidence = 0.5
        
        return {
            "symbol": symbol.upper(),
            "market": "BSE",
            "current_price": current.get('price'),
            "final_prediction": {
                "signal": final_signal,
                "confidence": round(confidence, 3)
            },
            "ml_prediction": ml_pred,
            "dl_prediction": dl_pred,
            "model_type": "Ensemble (ML + DL)"
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}
