"""
FINEX - Crypto Market Service
Fetches live data from Binance public API (no API key required)
"""
import httpx
from typing import Dict, List

BINANCE_BASE = "https://api.binance.com/api/v3"

# Pre-loaded list — grows when user clicks "Load More"
CRYPTO_SYMBOLS = [
    {"symbol": "BTCUSDT",  "name": "Bitcoin",        "short": "BTC"},
    {"symbol": "ETHUSDT",  "name": "Ethereum",       "short": "ETH"},
    {"symbol": "BNBUSDT",  "name": "BNB",            "short": "BNB"},
    {"symbol": "SOLUSDT",  "name": "Solana",         "short": "SOL"},
    {"symbol": "XRPUSDT",  "name": "XRP",            "short": "XRP"},
    {"symbol": "ADAUSDT",  "name": "Cardano",        "short": "ADA"},
    {"symbol": "DOGEUSDT", "name": "Dogecoin",       "short": "DOGE"},
    {"symbol": "DOTUSDT",  "name": "Polkadot",       "short": "DOT"},
    {"symbol": "MATICUSDT","name": "Polygon",        "short": "MATIC"},
    {"symbol": "LTCUSDT",  "name": "Litecoin",       "short": "LTC"},
    {"symbol": "AVAXUSDT", "name": "Avalanche",      "short": "AVAX"},
    {"symbol": "LINKUSDT", "name": "Chainlink",      "short": "LINK"},
    {"symbol": "UNIUSDT",  "name": "Uniswap",        "short": "UNI"},
    {"symbol": "ATOMUSDT", "name": "Cosmos",         "short": "ATOM"},
    {"symbol": "ETCUSDT",  "name": "Ethereum Classic","short": "ETC"},
    {"symbol": "XLMUSDT",  "name": "Stellar",        "short": "XLM"},
    {"symbol": "VETUSDT",  "name": "VeChain",        "short": "VET"},
    {"symbol": "ICPUSDT",  "name": "Internet Computer","short": "ICP"},
    {"symbol": "FILUSDT",  "name": "Filecoin",       "short": "FIL"},
    {"symbol": "TRXUSDT",  "name": "TRON",           "short": "TRX"},
    {"symbol": "NEARUSDT", "name": "NEAR Protocol",  "short": "NEAR"},
    {"symbol": "APTUSDT",  "name": "Aptos",          "short": "APT"},
    {"symbol": "ARBUSDT",  "name": "Arbitrum",       "short": "ARB"},
    {"symbol": "OPUSDT",   "name": "Optimism",       "short": "OP"},
    {"symbol": "SUIUSDT",  "name": "Sui",            "short": "SUI"},
    {"symbol": "SHIBUSDT", "name": "Shiba Inu",      "short": "SHIB"},
    {"symbol": "INJUSDT",  "name": "Injective",      "short": "INJ"},
    {"symbol": "RUNEUSDT", "name": "THORChain",      "short": "RUNE"},
    {"symbol": "AAVEUSDT", "name": "Aave",           "short": "AAVE"},
    {"symbol": "MKRUSDT",  "name": "Maker",          "short": "MKR"},
]

async def get_crypto_ticker(symbol: str) -> Dict:
    """Get 24hr ticker for a Binance symbol."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.get(f"{BINANCE_BASE}/ticker/24hr", params={"symbol": symbol})
            d = res.json()
            if "code" in d:
                return None
            meta = next((x for x in CRYPTO_SYMBOLS if x["symbol"] == symbol), {"name": symbol, "short": symbol})
            return {
                "symbol":         meta["short"],
                "binance_symbol": symbol,
                "name":           meta["name"],
                "price":          float(d.get("lastPrice", 0)),
                "change":         float(d.get("priceChange", 0)),
                "change_percent": float(d.get("priceChangePercent", 0)),
                "high":           float(d.get("highPrice", 0)),
                "low":            float(d.get("lowPrice", 0)),
                "volume":         float(d.get("volume", 0)),
                "quote_volume":   float(d.get("quoteVolume", 0)),
                "open":           float(d.get("openPrice", 0)),
            }
    except Exception as e:
        print(f"Binance ticker error {symbol}: {e}")
        return None

async def get_crypto_klines(symbol: str, interval: str = "1d", limit: int = 60) -> List[Dict]:
    """Get OHLCV candlestick data from Binance."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(f"{BINANCE_BASE}/klines", params={
                "symbol": symbol, "interval": interval, "limit": limit
            })
            data = res.json()
            if not isinstance(data, list):
                return []
            return [
                {
                    "time":   int(k[0]) // 1000,
                    "open":   float(k[1]),
                    "high":   float(k[2]),
                    "low":    float(k[3]),
                    "close":  float(k[4]),
                    "volume": float(k[5]),
                }
                for k in data
            ]
    except Exception as e:
        print(f"Binance klines error {symbol}: {e}")
        return []

async def get_all_crypto_tickers(page: int = 0, page_size: int = 10) -> List[Dict]:
    """Paginated: returns page_size tickers starting at offset page*page_size."""
    start = page * page_size
    batch = CRYPTO_SYMBOLS[start: start + page_size]
    results = []
    for meta in batch:
        t = await get_crypto_ticker(meta["symbol"])
        if t:
            results.append(t)
    return results