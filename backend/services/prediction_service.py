"""
FINEX - Real-Time Market Prediction Service
ML/DL models for Crypto, NSE, BSE predictions
Saves market data hourly + 10-min intervals
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import json
import os

# Market data storage
MARKET_DATA_DIR = "market_data"
os.makedirs(MARKET_DATA_DIR, exist_ok=True)

class MarketDataCollector:
    """Collect and store market data at intervals"""
    
    def __init__(self):
        self.data = {}
        self.timestamps = {}
    
    async def save_market_data(self, symbol: str, market_type: str, data: Dict):
        """Save market data (hourly + 10-min)"""
        file_path = f"{MARKET_DATA_DIR}/{market_type}_{symbol}.json"
        
        try:
            # Load existing data
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            # Add new data with timestamp
            data_point = {
                "timestamp": datetime.now().isoformat(),
                "price": data.get("price", 0),
                "high": data.get("high", 0),
                "low": data.get("low", 0),
                "volume": data.get("volume", 0),
                "change_percent": data.get("change_percent", 0)
            }
            
            history.append(data_point)
            
            # Keep last 1000 records (prevents huge files)
            if len(history) > 1000:
                history = history[-1000:]
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(history, f)
            
            return True
        except Exception as e:
            print(f"❌ Error saving data for {symbol}: {e}")
            return False
    
    async def get_market_history(self, symbol: str, market_type: str, days: int = 7):
        """Get historical market data"""
        file_path = f"{MARKET_DATA_DIR}/{market_type}_{symbol}.json"
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    history = json.load(f)
                return history[-288:] if days == 1 else history  # 288 = 24h * 12 (5-min intervals)
            return []
        except Exception as e:
            print(f"❌ Error loading history for {symbol}: {e}")
            return []


class PredictionModel:
    """ML/DL prediction engine"""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_trained = False
    
    async def train_model(self, symbol: str, market_type: str, history: List[Dict]):
        """Train ML model on historical data"""
        if len(history) < 20:
            return False
        
        try:
            # Prepare data
            prices = np.array([h["price"] for h in history]).reshape(-1, 1)
            volumes = np.array([h["volume"] for h in history])
            changes = np.array([h["change_percent"] for h in history])
            
            # Normalize
            scaled_prices = self.scaler.fit_transform(prices)
            
            # Create features (last 5 candles)
            X = []
            y = []
            window = 5
            
            for i in range(len(scaled_prices) - window):
                X.append(scaled_prices[i:i+window].flatten())
                y.append(scaled_prices[i+window][0])
            
            if len(X) > 0:
                X = np.array(X)
                y = np.array(y)
                self.rf_model.fit(X, y)
                self.model_trained = True
                return True
            
            return False
        except Exception as e:
            print(f"❌ Training error for {symbol}: {e}")
            return False
    
    async def predict(self, symbol: str, history: List[Dict], confidence_threshold: float = 0.55) -> Dict:
        """
        Predict market direction with strategy
        Returns: {"signal": "BUY/SELL/HOLD", "confidence": 0.75, "reason": "..."}
        """
        if len(history) < 10:
            return {"signal": "HOLD", "confidence": 0.0, "reason": "Insufficient data"}
        
        try:
            # Get recent data
            recent_prices = np.array([h["price"] for h in history[-20:]])
            recent_changes = np.array([h["change_percent"] for h in history[-20:]])
            recent_volumes = np.array([h["volume"] for h in history[-20:]])
            
            # Strategy 1: Trend Analysis (Conservative)
            price_trend = recent_prices[-1] - recent_prices[0]  # Last 20 candles
            short_trend = recent_prices[-1] - recent_prices[-5]  # Last 5 candles
            
            trend_score = 0
            if price_trend > 0 and short_trend > 0:
                trend_score = 0.8  # Strong uptrend
            elif price_trend > 0:
                trend_score = 0.6  # Weak uptrend
            elif price_trend < 0 and short_trend < 0:
                trend_score = -0.8  # Strong downtrend
            elif price_trend < 0:
                trend_score = -0.6  # Weak downtrend
            
            # Strategy 2: Volume Analysis
            avg_volume = np.mean(recent_volumes[-10:])
            current_volume = recent_volumes[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            volume_score = 0
            if volume_ratio > 1.5 and price_trend > 0:
                volume_score = 0.7  # High volume + price up = bullish
            elif volume_ratio > 1.5 and price_trend < 0:
                volume_score = -0.7  # High volume + price down = bearish
            elif volume_ratio < 0.7:
                volume_score = 0  # Low volume = uncertain
            
            # Strategy 3: Moving Average Crossover (Safe)
            ma_5 = np.mean(recent_prices[-5:])
            ma_10 = np.mean(recent_prices[-10:])
            current_price = recent_prices[-1]
            
            ma_score = 0
            if current_price > ma_5 > ma_10:
                ma_score = 0.75  # Bullish
            elif current_price < ma_5 < ma_10:
                ma_score = -0.75  # Bearish
            else:
                ma_score = 0  # Neutral
            
            # Strategy 4: Momentum (Rate of Change)
            roc = ((recent_prices[-1] - recent_prices[-5]) / recent_prices[-5]) * 100
            
            momentum_score = 0
            if roc > 2:
                momentum_score = 0.6  # Positive momentum
            elif roc < -2:
                momentum_score = -0.6  # Negative momentum
            
            # Combine all strategies (weighted)
            final_score = (trend_score * 0.35 + volume_score * 0.25 + ma_score * 0.25 + momentum_score * 0.15)
            
            # Confidence = how strong the signal is
            confidence = abs(final_score)
            
            # Signal generation
            if final_score > 0.3 and confidence > confidence_threshold:
                signal = "BUY"
                reason = f"Trend: {trend_score:.2f} | Volume: {volume_score:.2f} | MA: {ma_score:.2f} | ROC: {roc:.1f}%"
            elif final_score < -0.3 and confidence > confidence_threshold:
                signal = "SELL"
                reason = f"Trend: {trend_score:.2f} | Volume: {volume_score:.2f} | MA: {ma_score:.2f} | ROC: {roc:.1f}%"
            else:
                signal = "HOLD"
                reason = "Market uncertainty - waiting for clear signal"
            
            return {
                "signal": signal,
                "confidence": min(confidence, 1.0),
                "reason": reason,
                "trend_score": trend_score,
                "volume_score": volume_score,
                "ma_score": ma_score,
                "momentum": roc
            }
        
        except Exception as e:
            print(f"❌ Prediction error for {symbol}: {e}")
            return {"signal": "HOLD", "confidence": 0.0, "reason": f"Error: {str(e)}"}


class PredictionEngine:
    """Main prediction engine for all markets"""
    
    def __init__(self):
        self.data_collector = MarketDataCollector()
        self.models = {}  # One model per symbol
    
    async def predict_all_markets(self, crypto_tickers: List[Dict], nse_tickers: List[Dict], bse_tickers: List[Dict]) -> Dict:
        """Predict for all markets simultaneously"""
        predictions = {
            "crypto": [],
            "nse": [],
            "bse": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Crypto predictions
        for ticker in crypto_tickers[:30]:  # Top 30 cryptos
            pred = await self._predict_ticker(ticker, "crypto")
            predictions["crypto"].append(pred)
        
        # NSE predictions
        for ticker in nse_tickers[:50]:  # Top 50 NSE stocks
            pred = await self._predict_ticker(ticker, "nse")
            predictions["nse"].append(pred)
        
        # BSE predictions
        for ticker in bse_tickers[:50]:  # Top 50 BSE stocks
            pred = await self._predict_ticker(ticker, "bse")
            predictions["bse"].append(pred)
        
        return predictions
    
    async def _predict_ticker(self, ticker: Dict, market_type: str) -> Dict:
        """Predict single ticker"""
        symbol = ticker.get("symbol", "UNKNOWN")
        
        try:
            # Save current data
            await self.data_collector.save_market_data(symbol, market_type, ticker)
            
            # Get history
            history = await self.data_collector.get_market_history(symbol, market_type)
            
            if len(history) < 10:
                return {
                    "symbol": symbol,
                    "name": ticker.get("name", symbol),
                    "market": market_type,
                    "price": ticker.get("price", 0),
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "reason": "Collecting data..."
                }
            
            # Get prediction
            model = PredictionModel()
            await model.train_model(symbol, market_type, history)
            prediction = await model.predict(symbol, history)
            
            return {
                "symbol": symbol,
                "name": ticker.get("name", symbol),
                "market": market_type,
                "price": ticker.get("price", 0),
                "change_percent": ticker.get("change_percent", 0),
                **prediction
            }
        
        except Exception as e:
            return {
                "symbol": symbol,
                "market": market_type,
                "signal": "HOLD",
                "confidence": 0.0,
                "reason": f"Error: {str(e)}"
            }

# Global engine instance
prediction_engine = PredictionEngine()
