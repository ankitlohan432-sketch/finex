"""
FINEX - ML Predictions Service
Uses Random Forest & XGBoost for market direction prediction
Provides BUY/SELL/HOLD signals with confidence scores
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import logging
from typing import Dict, List, Tuple
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

# Models storage
MODELS_DIR = Path("models/ml")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class MLPredictor:
    """ML-based market predictions"""
    
    def __init__(self):
        self.rf_models = {}  # Random Forest models per symbol
        self.gb_models = {}  # Gradient Boosting models per symbol
        self.scalers = {}
        self.trained_symbols = set()
    
    def extract_features(self, historical_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract features from historical data
        Features: price change %, volume change, momentum, RSI, MACD
        """
        try:
            if len(historical_data) < 14:
                return None, None
            
            df = pd.DataFrame([
                {
                    'price': float(d['data'].get('price', 0)),
                    'volume': float(d['data'].get('volume', 0)),
                    'change_percent': float(d['data'].get('change_percent', 0)),
                    'high': float(d['data'].get('high', 0)),
                    'low': float(d['data'].get('low', 0))
                }
                for d in historical_data
            ])
            
            # Technical indicators
            df['price_change'] = df['price'].diff()
            df['volume_change'] = df['volume'].diff()
            df['price_momentum'] = df['price'].diff(5)  # 5-period momentum
            df['volatility'] = df['price'].rolling(14).std()
            df['sma_14'] = df['price'].rolling(14).mean()
            df['rsi'] = self._calculate_rsi(df['price'])
            
            # Target: 1 if price goes up, 0 if down (next period)
            df['target'] = (df['price'].shift(-1) > df['price']).astype(int)
            
            # Drop NaN
            df = df.dropna()
            
            features = df[['price_change', 'volume_change', 'price_momentum', 
                          'volatility', 'sma_14', 'rsi', 'change_percent']].values
            targets = df['target'].values
            
            return features, targets
        except Exception as e:
            logger.error(f"❌ Feature extraction failed: {e}")
            return None, None
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def train_model(self, symbol: str, market: str, historical_data: List[Dict]) -> bool:
        """Train RF and GB models for symbol"""
        try:
            features, targets = self.extract_features(historical_data)
            
            if features is None or len(features) < 20:
                logger.warning(f"⚠️ Insufficient data for {symbol}")
                return False
            
            # Normalize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Train Random Forest
            rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            rf.fit(features_scaled, targets)
            
            # Train Gradient Boosting
            gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
            gb.fit(features_scaled, targets)
            
            # Store models
            self.rf_models[symbol] = rf
            self.gb_models[symbol] = gb
            self.scalers[symbol] = scaler
            self.trained_symbols.add(symbol)
            
            logger.info(f"✅ Trained ML models for {symbol}")
            return True
        except Exception as e:
            logger.error(f"❌ Model training failed for {symbol}: {e}")
            return False
    
    def predict(self, symbol: str, current_data: Dict, historical_data: List[Dict]) -> Dict:
        """
        Predict market direction with confidence
        Returns: {signal: 'BUY'/'SELL'/'HOLD', confidence: 0.0-1.0, ml_score: float}
        """
        try:
            if symbol not in self.trained_symbols:
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Model not trained'}
            
            features, _ = self.extract_features(historical_data + [{'data': current_data}])
            
            if features is None or len(features) == 0:
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Insufficient data'}
            
            # Use last feature
            last_feature = features[-1:].reshape(1, -1)
            scaled = self.scalers[symbol].transform(last_feature)
            
            # Get predictions from both models
            rf_pred = self.rf_models[symbol].predict_proba(scaled)[0]  # [prob_down, prob_up]
            gb_pred = self.gb_models[symbol].predict_proba(scaled)[0]
            
            # Ensemble: average both models
            avg_prob_up = (rf_pred[1] + gb_pred[1]) / 2
            
            # Conservative signals (55%+ confidence = action, 45-55% = hold)
            if avg_prob_up >= 0.55:
                signal = 'BUY'
                confidence = min(avg_prob_up, 0.95)  # Cap at 95%
            elif avg_prob_up <= 0.45:
                signal = 'SELL'
                confidence = min(1 - avg_prob_up, 0.95)
            else:
                signal = 'HOLD'
                confidence = 0.5
            
            return {
                'signal': signal,
                'confidence': round(confidence, 3),
                'ml_score': round(avg_prob_up, 3),
                'rf_score': round(rf_pred[1], 3),
                'gb_score': round(gb_pred[1], 3)
            }
        except Exception as e:
            logger.error(f"❌ Prediction failed for {symbol}: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'error': str(e)}

# Global ML predictor
ml_predictor = MLPredictor()
