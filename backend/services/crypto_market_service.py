"""
FINEX - Crypto Market Service
Fetches live data from CoinGecko (free, no API key, works on Render)
Falls back to Binance if CoinGecko fails
"""
import httpx
from typing import Dict, List

BINANCE_BASE  = "https://api.binance.com/api/v3"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

CRYPTO_SYMBOLS = [
    {"symbol":"BTCUSDT",  "name":"Bitcoin",          "short":"BTC",  "cg_id":"bitcoin"},
    {"symbol":"ETHUSDT",  "name":"Ethereum",          "short":"ETH",  "cg_id":"ethereum"},
    {"symbol":"BNBUSDT",  "name":"BNB",               "short":"BNB",  "cg_id":"binancecoin"},
    {"symbol":"SOLUSDT",  "name":"Solana",            "short":"SOL",  "cg_id":"solana"},
    {"symbol":"XRPUSDT",  "name":"XRP",               "short":"XRP",  "cg_id":"ripple"},
    {"symbol":"ADAUSDT",  "name":"Cardano",           "short":"ADA",  "cg_id":"cardano"},
    {"symbol":"DOGEUSDT", "name":"Dogecoin",          "short":"DOGE", "cg_id":"dogecoin"},
    {"symbol":"DOTUSDT",  "name":"Polkadot",          "short":"DOT",  "cg_id":"polkadot"},
    {"symbol":"MATICUSDT","name":"Polygon",           "short":"MATIC","cg_id":"matic-network"},
    {"symbol":"LTCUSDT",  "name":"Litecoin",          "short":"LTC",  "cg_id":"litecoin"},
    {"symbol":"AVAXUSDT", "name":"Avalanche",         "short":"AVAX", "cg_id":"avalanche-2"},
    {"symbol":"LINKUSDT", "name":"Chainlink",         "short":"LINK", "cg_id":"chainlink"},
    {"symbol":"UNIUSDT",  "name":"Uniswap",           "short":"UNI",  "cg_id":"uniswap"},
    {"symbol":"ATOMUSDT", "name":"Cosmos",            "short":"ATOM", "cg_id":"cosmos"},
    {"symbol":"ETCUSDT",  "name":"Ethereum Classic",  "short":"ETC",  "cg_id":"ethereum-classic"},
    {"symbol":"XLMUSDT",  "name":"Stellar",           "short":"XLM",  "cg_id":"stellar"},
    {"symbol":"TRXUSDT",  "name":"TRON",              "short":"TRX",  "cg_id":"tron"},
    {"symbol":"NEARUSDT", "name":"NEAR Protocol",     "short":"NEAR", "cg_id":"near"},
    {"symbol":"APTUSDT",  "name":"Aptos",             "short":"APT",  "cg_id":"aptos"},
    {"symbol":"ARBUSDT",  "name":"Arbitrum",          "short":"ARB",  "cg_id":"arbitrum"},
    {"symbol":"OPUSDT",   "name":"Optimism",          "short":"OP",   "cg_id":"optimism"},
    {"symbol":"SUIUSDT",  "name":"Sui",               "short":"SUI",  "cg_id":"sui"},
    {"symbol":"SHIBUSDT", "name":"Shiba Inu",         "short":"SHIB", "cg_id":"shiba-inu"},
    {"symbol":"INJUSDT",  "name":"Injective",         "short":"INJ",  "cg_id":"injective-protocol"},
    {"symbol":"AAVEUSDT", "name":"Aave",              "short":"AAVE", "cg_id":"aave"},
    {"symbol":"MKRUSDT",  "name":"Maker",             "short":"MKR",  "cg_id":"maker"},
    {"symbol":"RUNEUSDT", "name":"THORChain",         "short":"RUNE", "cg_id":"thorchain"},
    {"symbol":"FILUSDT",  "name":"Filecoin",          "short":"FIL",  "cg_id":"filecoin"},
    {"symbol":"ICPUSDT",  "name":"Internet Computer", "short":"ICP",  "cg_id":"internet-computer"},
    {"symbol":"VETUSDT",  "name":"VeChain",           "short":"VET",  "cg_id":"vechain"},
]

CG_ID_MAP = {c["symbol"]: c["cg_id"] for c in CRYPTO_SYMBOLS}
META_MAP   = {c["symbol"]: c for c in CRYPTO_SYMBOLS}

async def get_all_crypto_tickers(page: int = 0, page_size: int = 10) -> List[Dict]:
    start = page * page_size
    batch = CRYPTO_SYMBOLS[start: start + page_size]
    if not batch:
        return []
    cg_ids = [c["cg_id"] for c in batch]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(
                f"{COINGECKO_BASE}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "ids": ",".join(cg_ids),
                    "order": "market_cap_desc",
                    "per_page": page_size,
                    "page": 1,
                    "sparkline": False,
                    "price_change_percentage": "24h"
                }
            )
            if res.status_code != 200:
                raise Exception(f"CoinGecko {res.status_code}")
            data = res.json()
            results = []
            for coin in data:
                sym = next((c["symbol"] for c in CRYPTO_SYMBOLS if c["cg_id"] == coin["id"]), None)
                if not sym:
                    continue
                results.append({
                    "symbol":         META_MAP.get(sym, {}).get("short", sym),
                    "binance_symbol": sym,
                    "name":           coin.get("name", sym),
                    "price":          coin.get("current_price", 0) or 0,
                    "change":         coin.get("price_change_24h", 0) or 0,
                    "change_percent": coin.get("price_change_percentage_24h", 0) or 0,
                    "high":           coin.get("high_24h", 0) or 0,
                    "low":            coin.get("low_24h", 0) or 0,
                    "volume":         coin.get("total_volume", 0) or 0,
                    "quote_volume":   coin.get("total_volume", 0) or 0,
                    "open":           (coin.get("current_price", 0) or 0) - (coin.get("price_change_24h", 0) or 0),
                    "market_cap":     coin.get("market_cap", 0) or 0,
                    "image":          coin.get("image", ""),
                })
            return results
    except Exception as e:
        print(f"CoinGecko error, falling back to Binance: {e}")
        return await _binance_fallback(batch)

async def _binance_fallback(batch) -> List[Dict]:
    results = []
    for meta in batch:
        t = await get_crypto_ticker(meta["symbol"])
        if t:
            results.append(t)
    return results

async def get_crypto_ticker(symbol: str) -> Dict:
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.get(f"{BINANCE_BASE}/ticker/24hr", params={"symbol": symbol})
            d = res.json()
            if "code" in d:
                return None
            meta = META_MAP.get(symbol, {"name": symbol, "short": symbol})
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
                "market_cap":     0,
                "image":          "",
            }
    except Exception as e:
        print(f"Binance ticker error {symbol}: {e}")
        return None

async def get_crypto_klines(symbol: str, interval: str = "1d", limit: int = 60) -> List[Dict]:
    # Always use Binance for klines (chart data) — works fine
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
