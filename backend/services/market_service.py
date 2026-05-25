from typing import List, Dict
from config import settings
import httpx

class MarketService:
    def __init__(self):
        self.api_key = settings.STOCK_API_KEY
        self.base_url = "https://api.twelvedata.com"

    async def get_stock_price(self, symbol: str) -> Dict:
        if not self.api_key:
            return {"symbol": symbol, "price": 0, "change": 0, "change_percent": 0, "name": symbol}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.get(f"{self.base_url}/quote", params={"symbol": symbol, "apikey": self.api_key})
                d = res.json()
                if d.get("status") == "error" or "code" in d:
                    return {"symbol": symbol, "price": 0, "change": 0, "change_percent": 0, "name": symbol}
                return {
                    "symbol": symbol,
                    "name": d.get("name", symbol),
                    "price": float(d.get("close", 0) or 0),
                    "change": float(d.get("change", 0) or 0),
                    "change_percent": float(d.get("percent_change", 0) or 0),
                    "volume": int(d.get("volume", 0) or 0),
                    "high": float(d.get("high", 0) or 0),
                    "low": float(d.get("low", 0) or 0),
                    "open": float(d.get("open", 0) or 0),
                    "fifty_two_week_high": float(d.get("fifty_two_week", {}).get("high", 0) or 0),
                    "fifty_two_week_low": float(d.get("fifty_two_week", {}).get("low", 0) or 0),
                }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return {"symbol": symbol, "price": 0, "change": 0, "change_percent": 0, "name": symbol}

    async def get_stock_history(self, symbol: str, interval: str = "1day") -> List[Dict]:
        if not self.api_key:
            return []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.get(f"{self.base_url}/time_series", params={
                    "symbol": symbol, "interval": interval, "outputsize": 30, "apikey": self.api_key
                })
                d = res.json()
                values = d.get("values", [])
                return [{"date": v["datetime"], "open": float(v["open"]), "high": float(v["high"]),
                         "low": float(v["low"]), "close": float(v["close"]), "volume": int(v.get("volume", 0))}
                        for v in values]
        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return []

    async def get_top_movers(self) -> List[Dict]:
        symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "NFLX"]
        results = []
        for symbol in symbols:
            data = await self.get_stock_price(symbol)
            if data.get("price", 0) > 0:
                results.append(data)
        return sorted(results, key=lambda x: abs(x.get("change_percent", 0)), reverse=True)

    async def get_market_overview(self) -> Dict:
        # Return mock indices + real top movers
        top_movers = await self.get_top_movers()
        gainers = [s for s in top_movers if s.get("change_percent", 0) > 0]
        losers = [s for s in top_movers if s.get("change_percent", 0) < 0]
        return {
            "indices": [
                {"name": "NIFTY 50", "value": 21847.90, "change": 0.68, "change_percent": 0.68},
                {"name": "SENSEX", "value": 72240.26, "change": 0.73, "change_percent": 0.73},
                {"name": "BANK NIFTY", "value": 46892.35, "change": 0.47, "change_percent": 0.47},
                {"name": "NASDAQ", "value": 17890.78, "change": 1.2, "change_percent": 1.2},
            ],
            "top_gainers": gainers[:3],
            "top_losers": losers[:3],
        }

market_service = MarketService()
