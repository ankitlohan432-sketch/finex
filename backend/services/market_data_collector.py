"""
FINEX - Market Data Collector
Collects and stores market data at 10min and hourly intervals
Used for ML/DL model training and real-time predictions
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Data storage paths
DATA_DIR = Path("data/market_snapshots")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class MarketDataCollector:
    """Collects market data for all symbols (crypto, NSE, BSE)"""
    
    def __init__(self):
        self.data_cache = {}
        self.last_collection_time = {}
    
    def save_snapshot(self, market: str, symbol: str, data: Dict):
        """
        Save market snapshot for symbol
        market: 'crypto', 'nse', 'bse'
        """
        try:
            timestamp = datetime.now()
            hour = timestamp.strftime("%Y-%m-%d_%H")
            
            # Create directory structure: data/crypto/BTCUSDT/2024-05-24_10/
            symbol_dir = DATA_DIR / market / symbol / hour
            symbol_dir.mkdir(parents=True, exist_ok=True)
            
            # Save with 10-min precision filename
            minute = (timestamp.minute // 10) * 10
            filename = f"{timestamp.strftime('%Y%m%d')}_{timestamp.hour:02d}{minute:02d}.json"
            filepath = symbol_dir / filename
            
            # Add metadata
            data_with_meta = {
                "timestamp": timestamp.isoformat(),
                "symbol": symbol,
                "market": market,
                "data": data
            }
            
            # Append to file (keep history)
            with open(filepath, 'a') as f:
                f.write(json.dumps(data_with_meta) + "\n")
            
            logger.info(f"✅ Saved {market}/{symbol} snapshot at {timestamp}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save snapshot {market}/{symbol}: {e}")
            return False
    
    def get_historical_data(self, market: str, symbol: str, hours: int = 24) -> List[Dict]:
        """
        Get historical data for symbol (last N hours)
        Returns list of snapshots with timestamps
        """
        try:
            data = []
            now = datetime.now()
            
            for h in range(hours):
                check_time = now - timedelta(hours=h)
                hour_str = check_time.strftime("%Y-%m-%d_%H")
                symbol_dir = DATA_DIR / market / symbol / hour_str
                
                if symbol_dir.exists():
                    for file in sorted(symbol_dir.glob("*.json")):
                        with open(file, 'r') as f:
                            for line in f:
                                data.append(json.loads(line))
            
            return sorted(data, key=lambda x: x['timestamp'])
        except Exception as e:
            logger.error(f"❌ Failed to get historical data {market}/{symbol}: {e}")
            return []
    
    def get_latest_snapshot(self, market: str, symbol: str) -> Dict:
        """Get most recent snapshot for symbol"""
        try:
            now = datetime.now()
            
            # Check last 2 hours for latest data
            for h in range(2):
                check_time = now - timedelta(hours=h)
                hour_str = check_time.strftime("%Y-%m-%d_%H")
                symbol_dir = DATA_DIR / market / symbol / hour_str
                
                if symbol_dir.exists():
                    files = sorted(symbol_dir.glob("*.json"))
                    if files:
                        with open(files[-1], 'r') as f:
                            lines = f.readlines()
                            if lines:
                                return json.loads(lines[-1])
            
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get latest snapshot {market}/{symbol}: {e}")
            return None
    
    async def collect_all_markets(self, 
                                  crypto_tickers_func,
                                  nse_tickers_func, 
                                  bse_tickers_func):
        """
        Collect data from all markets
        Run every 10 minutes
        """
        try:
            logger.info("📊 Starting market data collection...")
            
            # Collect Crypto
            crypto_data = await crypto_tickers_func(page=0, page_size=30)
            for ticker in crypto_data.get('data', []):
                self.save_snapshot('crypto', ticker['binance_symbol'], ticker)
            
            # Collect NSE
            nse_data = await nse_tickers_func(page=0, page_size=50)
            for ticker in nse_data.get('data', []):
                self.save_snapshot('nse', ticker['symbol'], ticker)
            
            # Collect BSE
            bse_data = await bse_tickers_func(page=0, page_size=50)
            for ticker in bse_data.get('data', []):
                self.save_snapshot('bse', ticker['symbol'], ticker)
            
            logger.info("✅ Market data collection complete!")
        except Exception as e:
            logger.error(f"❌ Collection failed: {e}")

# Global collector instance
market_collector = MarketDataCollector()
