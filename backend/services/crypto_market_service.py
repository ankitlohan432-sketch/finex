import httpx
import asyncio
import time
from typing import Dict, List

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
COINCAP_BASE   = "https://api.coincap.io/v2"

CRYPTO_SYMBOLS = [
    {"symbol":"bitcoin",          "name":"Bitcoin",            "short":"BTC",  "cap_id":"bitcoin"},
    {"symbol":"ethereum",         "name":"Ethereum",           "short":"ETH",  "cap_id":"ethereum"},
    {"symbol":"binancecoin",      "name":"BNB",                "short":"BNB",  "cap_id":"binance-coin"},
    {"symbol":"solana",           "name":"Solana",             "short":"SOL",  "cap_id":"solana"},
    {"symbol":"ripple",           "name":"XRP",                "short":"XRP",  "cap_id":"xrp"},
    {"symbol":"cardano",          "name":"Cardano",            "short":"ADA",  "cap_id":"cardano"},
    {"symbol":"dogecoin",         "name":"Dogecoin",           "short":"DOGE", "cap_id":"dogecoin"},
    {"symbol":"polkadot",         "name":"Polkadot",           "short":"DOT",  "cap_id":"polkadot"},
    {"symbol":"matic-network",    "name":"Polygon",            "short":"MATIC","cap_id":"polygon"},
    {"symbol":"litecoin",         "name":"Litecoin",           "short":"LTC",  "cap_id":"litecoin"},
    {"symbol":"avalanche-2",      "name":"Avalanche",          "short":"AVAX", "cap_id":"avalanche"},
    {"symbol":"chainlink",        "name":"Chainlink",          "short":"LINK", "cap_id":"chainlink"},
    {"symbol":"uniswap",          "name":"Uniswap",            "short":"UNI",  "cap_id":"uniswap"},
    {"symbol":"cosmos",           "name":"Cosmos",             "short":"ATOM", "cap_id":"cosmos"},
    {"symbol":"stellar",          "name":"Stellar",            "short":"XLM",  "cap_id":"stellar"},
    {"symbol":"tron",             "name":"TRON",               "short":"TRX",  "cap_id":"tron"},
    {"symbol":"near",             "name":"NEAR Protocol",      "short":"NEAR", "cap_id":"near-protocol"},
    {"symbol":"arbitrum",         "name":"Arbitrum",           "short":"ARB",  "cap_id":"arbitrum"},
    {"symbol":"optimism",         "name":"Optimism",           "short":"OP",   "cap_id":"optimism"},
    {"symbol":"sui",              "name":"Sui",                "short":"SUI",  "cap_id":"sui"},
    {"symbol":"shiba-inu",        "name":"Shiba Inu",          "short":"SHIB", "cap_id":"shiba-inu"},
    {"symbol":"injective-protocol","name":"Injective",         "short":"INJ",  "cap_id":"injective-protocol"},
    {"symbol":"aave",             "name":"Aave",               "short":"AAVE", "cap_id":"aave"},
    {"symbol":"filecoin",         "name":"Filecoin",           "short":"FIL",  "cap_id":"filecoin"},
    {"symbol":"internet-computer","name":"Internet Computer",  "short":"ICP",  "cap_id":"internet-computer"},
    {"symbol":"vechain",          "name":"VeChain",            "short":"VET",  "cap_id":"vechain"},
    {"symbol":"the-graph",        "name":"The Graph",          "short":"GRT",  "cap_id":"the-graph"},
    {"symbol":"algorand",         "name":"Algorand",           "short":"ALGO", "cap_id":"algorand"},
    {"symbol":"fantom",           "name":"Fantom",             "short":"FTM",  "cap_id":"fantom"},
    {"symbol":"the-sandbox",      "name":"The Sandbox",        "short":"SAND", "cap_id":"the-sandbox"},
    {"symbol":"decentraland",     "name":"Decentraland",       "short":"MANA", "cap_id":"decentraland"},
    {"symbol":"axie-infinity",    "name":"Axie Infinity",      "short":"AXS",  "cap_id":"axie-infinity"},
    {"symbol":"hedera-hashgraph", "name":"Hedera",             "short":"HBAR", "cap_id":"hedera-hashgraph"},
    {"symbol":"lido-dao",         "name":"Lido DAO",           "short":"LDO",  "cap_id":"lido-dao"},
    {"symbol":"render-token",     "name":"Render",             "short":"RNDR", "cap_id":"render-token"},
    {"symbol":"worldcoin-wld",    "name":"Worldcoin",          "short":"WLD",  "cap_id":"worldcoin"},
    {"symbol":"stacks",           "name":"Stacks",             "short":"STX",  "cap_id":"blockstack"},
    {"symbol":"fetch-ai",         "name":"Fetch.ai",           "short":"FET",  "cap_id":"fetch-ai"},
    {"symbol":"stepn",            "name":"STEPN",              "short":"GMT",  "cap_id":"stepn"},
    {"symbol":"curve-dao-token",  "name":"Curve DAO",          "short":"CRV",  "cap_id":"curve-dao-token"},
]

META_MAP   = {c["symbol"]: c for c in CRYPTO_SYMBOLS}
CAP_ID_MAP = {c["cap_id"]: c for c in CRYPTO_SYMBOLS}

# Rate limiting - CoinGecko 30 calls/min
_cg_last_call: float = 0
_CG_MIN_INTERVAL = 2.0

# Cache - 5 minutes = 288 calls/day = safe all month
_ticker_cache: Dict = {}
_ticker_cache_time: float = 0
_TICKER_TTL = 300

async def _cg_get(url, params):
    global _cg_last_call
    wait = _CG_MIN_INTERVAL - (time.time() - _cg_last_call)
    if wait > 0:
        await asyncio.sleep(wait)
    _cg_last_call = time.time()
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        return res

async def get_all_crypto_tickers(page: int = 0, page_size: int = 10) -> List[Dict]:
    global _ticker_cache, _ticker_cache_time
    start = page * page_size
    batch = CRYPTO_SYMBOLS[start: start + page_size]
    if not batch:
        return []

    cache_key = f"{page}_{page_size}"
    if cache_key in _ticker_cache and time.time() - _ticker_cache_time < _TICKER_TTL:
        return _ticker_cache[cache_key]

    ids = ",".join([c["symbol"] for c in batch])
    try:
        res = await _cg_get(
            f"{COINGECKO_BASE}/coins/markets",
            {
                "vs_currency": "usd",
                "ids": ids,
                "order": "market_cap_desc",
                "per_page": page_size,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h",
            }
        )
        if res.status_code == 429:
            return await _coincap_fallback(batch)
        if res.status_code != 200:
            return await _coincap_fallback(batch)

        results = []
        for coin in res.json():
            cg_id = coin.get("id")
            meta  = META_MAP.get(cg_id, {"name": coin.get("name"), "short": coin.get("symbol","").upper()})
            results.append({
                "symbol":         meta["short"],
                "binance_symbol": meta["short"] + "USDT",
                "name":           meta["name"],
                "price":          float(coin.get("current_price") or 0),
                "change":         float(coin.get("price_change_24h") or 0),
                "change_percent": float(coin.get("price_change_percentage_24h") or 0),
                "high":           float(coin.get("high_24h") or 0),
                "low":            float(coin.get("low_24h") or 0),
                "volume":         float(coin.get("total_volume") or 0),
                "quote_volume":   float(coin.get("total_volume") or 0),
                "market_cap":     float(coin.get("market_cap") or 0),
                "image":          coin.get("image", ""),
            })
        _ticker_cache[cache_key] = results
        _ticker_cache_time = time.time()
        return results
    except Exception as e:
        print(f"CoinGecko error: {e}")
        return await _coincap_fallback(batch)

async def _coincap_fallback(batch) -> List[Dict]:
    try:
        ids = ",".join([c["cap_id"] for c in batch])
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(f"{COINCAP_BASE}/assets", params={"ids": ids, "limit": len(batch)})
            if res.status_code != 200:
                return []
            results = []
            for coin in res.json().get("data", []):
                meta   = CAP_ID_MAP.get(coin.get("id"), {"name": coin.get("name"), "short": coin.get("symbol","")})
                price  = float(coin.get("priceUsd") or 0)
                change = float(coin.get("changePercent24Hr") or 0)
                vol    = float(coin.get("volumeUsd24Hr") or 0)
                results.append({
                    "symbol":         meta["short"],
                    "binance_symbol": meta["short"] + "USDT",
                    "name":           meta["name"],
                    "price":          price,
                    "change":         price * change / 100,
                    "change_percent": change,
                    "high":           0,
                    "low":            0,
                    "volume":         vol,
                    "quote_volume":   vol,
                    "market_cap":     float(coin.get("marketCapUsd") or 0),
                    "image":          "",
                })
            return results
    except Exception as e:
        print(f"CoinCap error: {e}")
        return []

async def get_crypto_ticker(symbol: str) -> Dict:
    try:
        res = await _cg_get(
            f"{COINGECKO_BASE}/simple/price",
            {"ids": symbol, "vs_currencies": "usd", "include_24hr_change": True, "include_24hr_vol": True}
        )
        if res.status_code == 200:
            data = res.json().get(symbol, {})
            meta = META_MAP.get(symbol, {"name": symbol, "short": symbol.upper()})
            return {
                "symbol":         meta["short"],
                "name":           meta["name"],
                "price":          float(data.get("usd") or 0),
                "change_percent": float(data.get("usd_24h_change") or 0),
                "volume":         float(data.get("usd_24h_vol") or 0),
                "market_cap":     0,
                "image":          "",
            }
    except Exception as e:
        print(f"Ticker error {symbol}: {e}")
    return None

async def get_crypto_klines(symbol: str, interval: str = "1d", limit: int = 60) -> List[Dict]:
    try:
        days_map = {"5m": 1, "15m": 1, "1h": 7, "4h": 14, "1d": 60, "1wk": 180}
        days = days_map.get(interval, 7)
        res = await _cg_get(
            f"{COINGECKO_BASE}/coins/{symbol}/ohlc",
            {"vs_currency": "usd", "days": days}
        )
        if res.status_code != 200:
            return []
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
                "volume": 0,
            }
            for k in data[-limit:]
        ]
    except Exception as e:
        print(f"CoinGecko klines error {symbol}: {e}")
        return []
