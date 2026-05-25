import httpx
import asyncio
import time
from typing import Dict, List

COINGECKO_BASE   = "https://api.coingecko.com/api/v3"
CRYPTOCOMPARE_BASE = "https://min-api.cryptocompare.com/data"

CRYPTO_SYMBOLS = [
    {"symbol":"bitcoin",          "name":"Bitcoin",            "short":"BTC"},
    {"symbol":"ethereum",         "name":"Ethereum",           "short":"ETH"},
    {"symbol":"binancecoin",      "name":"BNB",                "short":"BNB"},
    {"symbol":"solana",           "name":"Solana",             "short":"SOL"},
    {"symbol":"ripple",           "name":"XRP",                "short":"XRP"},
    {"symbol":"cardano",          "name":"Cardano",            "short":"ADA"},
    {"symbol":"dogecoin",         "name":"Dogecoin",           "short":"DOGE"},
    {"symbol":"polkadot",         "name":"Polkadot",           "short":"DOT"},
    {"symbol":"matic-network",    "name":"Polygon",            "short":"MATIC"},
    {"symbol":"litecoin",         "name":"Litecoin",           "short":"LTC"},
    {"symbol":"avalanche-2",      "name":"Avalanche",          "short":"AVAX"},
    {"symbol":"chainlink",        "name":"Chainlink",          "short":"LINK"},
    {"symbol":"uniswap",          "name":"Uniswap",            "short":"UNI"},
    {"symbol":"cosmos",           "name":"Cosmos",             "short":"ATOM"},
    {"symbol":"stellar",          "name":"Stellar",            "short":"XLM"},
    {"symbol":"tron",             "name":"TRON",               "short":"TRX"},
    {"symbol":"near",             "name":"NEAR Protocol",      "short":"NEAR"},
    {"symbol":"arbitrum",         "name":"Arbitrum",           "short":"ARB"},
    {"symbol":"optimism",         "name":"Optimism",           "short":"OP"},
    {"symbol":"sui",              "name":"Sui",                "short":"SUI"},
    {"symbol":"shiba-inu",        "name":"Shiba Inu",          "short":"SHIB"},
    {"symbol":"injective-protocol","name":"Injective",         "short":"INJ"},
    {"symbol":"aave",             "name":"Aave",               "short":"AAVE"},
    {"symbol":"filecoin",         "name":"Filecoin",           "short":"FIL"},
    {"symbol":"internet-computer","name":"Internet Computer",  "short":"ICP"},
    {"symbol":"vechain",          "name":"VeChain",            "short":"VET"},
    {"symbol":"the-graph",        "name":"The Graph",          "short":"GRT"},
    {"symbol":"algorand",         "name":"Algorand",           "short":"ALGO"},
    {"symbol":"fantom",           "name":"Fantom",             "short":"FTM"},
    {"symbol":"the-sandbox",      "name":"The Sandbox",        "short":"SAND"},
    {"symbol":"decentraland",     "name":"Decentraland",       "short":"MANA"},
    {"symbol":"axie-infinity",    "name":"Axie Infinity",      "short":"AXS"},
    {"symbol":"hedera-hashgraph", "name":"Hedera",             "short":"HBAR"},
    {"symbol":"lido-dao",         "name":"Lido DAO",           "short":"LDO"},
    {"symbol":"render-token",     "name":"Render",             "short":"RNDR"},
    {"symbol":"worldcoin-wld",    "name":"Worldcoin",          "short":"WLD"},
    {"symbol":"stacks",           "name":"Stacks",             "short":"STX"},
    {"symbol":"fetch-ai",         "name":"Fetch.ai",           "short":"FET"},
    {"symbol":"stepn",            "name":"STEPN",              "short":"GMT"},
    {"symbol":"curve-dao-token",  "name":"Curve DAO",          "short":"CRV"},
]

META_MAP    = {c["symbol"]: c for c in CRYPTO_SYMBOLS}
SHORT_MAP   = {c["short"]: c for c in CRYPTO_SYMBOLS}

# Rate limiting
_cg_last_call: float = 0
_CG_MIN_INTERVAL = 2.0

# Cache 10 minutes = safe all month
_ticker_cache: Dict = {}
_ticker_cache_time: float = 0
_TICKER_TTL = 600

async def _cg_get(url, params):
    global _cg_last_call
    wait = _CG_MIN_INTERVAL - (time.time() - _cg_last_call)
    if wait > 0:
        await asyncio.sleep(wait)
    _cg_last_call = time.time()
    async with httpx.AsyncClient(timeout=15) as client:
        return await client.get(url, params=params)

async def _cryptocompare_fallback(batch) -> List[Dict]:
    """CryptoCompare - free, no geo restrictions, very generous limits"""
    try:
        shorts = ",".join([c["short"] for c in batch])
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                f"{CRYPTOCOMPARE_BASE}/pricemultifull",
                params={"fsyms": shorts, "tsyms": "USD"}
            )
            if res.status_code != 200:
                return []
            data = res.json().get("RAW", {})
            results = []
            for short, info in data.items():
                usd = info.get("USD", {})
                meta = SHORT_MAP.get(short, {"name": short, "short": short, "symbol": short})
                results.append({
                    "symbol":         short,
                    "binance_symbol": short + "USDT",
                    "name":           meta["name"],
                    "price":          float(usd.get("PRICE") or 0),
                    "change":         float(usd.get("CHANGE24HOUR") or 0),
                    "change_percent": float(usd.get("CHANGEPCT24HOUR") or 0),
                    "high":           float(usd.get("HIGH24HOUR") or 0),
                    "low":            float(usd.get("LOW24HOUR") or 0),
                    "volume":         float(usd.get("VOLUME24HOURTO") or 0),
                    "quote_volume":   float(usd.get("VOLUME24HOURTO") or 0),
                    "market_cap":     float(usd.get("MKTCAP") or 0),
                    "image":          f"https://www.cryptocompare.com{usd.get('IMAGEURL', '')}",
                })
            return results
    except Exception as e:
        print(f"CryptoCompare error: {e}")
        return []

async def get_all_crypto_tickers(page: int = 0, page_size: int = 10) -> List[Dict]:
    global _ticker_cache, _ticker_cache_time
    start = page * page_size
    batch = CRYPTO_SYMBOLS[start: start + page_size]
    if not batch:
        return []

    cache_key = f"{page}_{page_size}"
    if cache_key in _ticker_cache and time.time() - _ticker_cache_time < _TICKER_TTL:
        return _ticker_cache[cache_key]

    # Try CoinGecko first
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
        if res.status_code == 200:
            results = []
            for coin in res.json():
                cg_id = coin.get("id")
                meta  = META_MAP.get(cg_id, {"name": coin.get("name"), "short": coin.get("symbol","").upper()})
                results.append({
                    "symbol":         meta["short"],
                    "binance_symbol": meta["short"] + "USDT",
                    "cg_id": cg_id,
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

    # Fallback to CryptoCompare
    print("Falling back to CryptoCompare...")
    results = await _cryptocompare_fallback(batch)
    if results:
        _ticker_cache[cache_key] = results
        _ticker_cache_time = time.time()
    return results

async def get_crypto_ticker(symbol: str) -> Dict:
    try:
        res = await _cg_get(
            f"{COINGECKO_BASE}/simple/price",
            {"ids": symbol, "vs_currencies": "usd", "include_24hr_change": True}
        )
        if res.status_code == 200:
            data = res.json().get(symbol, {})
            meta = META_MAP.get(symbol, {"name": symbol, "short": symbol.upper()})
            return {
                "symbol":         meta["short"],
                "name":           meta["name"],
                "price":          float(data.get("usd") or 0),
                "change_percent": float(data.get("usd_24h_change") or 0),
                "volume":         0,
                "market_cap":     0,
                "image":          "",
            }
    except Exception as e:
        print(f"Ticker error {symbol}: {e}")
    return None

BINANCE_TO_CG = {c["short"]+"USDT": c["symbol"] for c in CRYPTO_SYMBOLS}
SHORT_TO_CG   = {c["short"]: c["symbol"] for c in CRYPTO_SYMBOLS}

async def get_crypto_klines(symbol: str, interval: str = "1d", limit: int = 60) -> List[Dict]:
    cg_symbol = BINANCE_TO_CG.get(symbol.upper()) or SHORT_TO_CG.get(symbol.upper()) or symbol.lower()
    symbol = cg_symbol
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
        print(f"Klines error {symbol}: {e}")
        return []


