import httpx
import asyncio
import time
from typing import Dict, List

BINANCE_BASE   = "https://api.binance.com/api/v3"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

CRYPTO_SYMBOLS = [
    {"symbol":"BTCUSDT",   "name":"Bitcoin",           "short":"BTC"},
    {"symbol":"ETHUSDT",   "name":"Ethereum",          "short":"ETH"},
    {"symbol":"BNBUSDT",   "name":"BNB",               "short":"BNB"},
    {"symbol":"SOLUSDT",   "name":"Solana",            "short":"SOL"},
    {"symbol":"XRPUSDT",   "name":"XRP",               "short":"XRP"},
    {"symbol":"ADAUSDT",   "name":"Cardano",           "short":"ADA"},
    {"symbol":"DOGEUSDT",  "name":"Dogecoin",          "short":"DOGE"},
    {"symbol":"DOTUSDT",   "name":"Polkadot",          "short":"DOT"},
    {"symbol":"MATICUSDT", "name":"Polygon",           "short":"MATIC"},
    {"symbol":"LTCUSDT",   "name":"Litecoin",          "short":"LTC"},
    {"symbol":"AVAXUSDT",  "name":"Avalanche",         "short":"AVAX"},
    {"symbol":"LINKUSDT",  "name":"Chainlink",         "short":"LINK"},
    {"symbol":"UNIUSDT",   "name":"Uniswap",           "short":"UNI"},
    {"symbol":"ATOMUSDT",  "name":"Cosmos",            "short":"ATOM"},
    {"symbol":"ETCUSDT",   "name":"Ethereum Classic",  "short":"ETC"},
    {"symbol":"XLMUSDT",   "name":"Stellar",           "short":"XLM"},
    {"symbol":"TRXUSDT",   "name":"TRON",              "short":"TRX"},
    {"symbol":"NEARUSDT",  "name":"NEAR Protocol",     "short":"NEAR"},
    {"symbol":"ARBUSDT",   "name":"Arbitrum",          "short":"ARB"},
    {"symbol":"OPUSDT",    "name":"Optimism",          "short":"OP"},
    {"symbol":"SUIUSDT",   "name":"Sui",               "short":"SUI"},
    {"symbol":"SHIBUSDT",  "name":"Shiba Inu",         "short":"SHIB"},
    {"symbol":"INJUSDT",   "name":"Injective",         "short":"INJ"},
    {"symbol":"AAVEUSDT",  "name":"Aave",              "short":"AAVE"},
    {"symbol":"MKRUSDT",   "name":"Maker",             "short":"MKR"},
    {"symbol":"FILUSDT",   "name":"Filecoin",          "short":"FIL"},
    {"symbol":"ICPUSDT",   "name":"Internet Computer", "short":"ICP"},
    {"symbol":"VETUSDT",   "name":"VeChain",           "short":"VET"},
    {"symbol":"GRTUSDT",   "name":"The Graph",         "short":"GRT"},
    {"symbol":"ALGOUSDT",  "name":"Algorand",          "short":"ALGO"},
    {"symbol":"FTMUSDT",   "name":"Fantom",            "short":"FTM"},
    {"symbol":"SANDUSDT",  "name":"The Sandbox",       "short":"SAND"},
    {"symbol":"MANAUSDT",  "name":"Decentraland",      "short":"MANA"},
    {"symbol":"AXSUSDT",   "name":"Axie Infinity",     "short":"AXS"},
    {"symbol":"HBARUSDT",  "name":"Hedera",            "short":"HBAR"},
    {"symbol":"CHZUSDT",   "name":"Chiliz",            "short":"CHZ"},
    {"symbol":"APEUSDT",   "name":"ApeCoin",           "short":"APE"},
    {"symbol":"GALAUSDT",  "name":"Gala",              "short":"GALA"},
    {"symbol":"CRVUSDT",   "name":"Curve DAO",         "short":"CRV"},
    {"symbol":"LDOUSDT",   "name":"Lido DAO",          "short":"LDO"},
    {"symbol":"FETUSDT",   "name":"Fetch.ai",          "short":"FET"},
    {"symbol":"RNDRUSDT",  "name":"Render",            "short":"RNDR"},
    {"symbol":"WLDUSDT",   "name":"Worldcoin",         "short":"WLD"},
    {"symbol":"PENDLEUSDT","name":"Pendle",            "short":"PENDLE"},
    {"symbol":"JUPUSDT",   "name":"Jupiter",           "short":"JUP"},
    {"symbol":"SEIUSDT",   "name":"Sei",               "short":"SEI"},
    {"symbol":"PYTHUSDT",  "name":"Pyth Network",      "short":"PYTH"},
    {"symbol":"STXUSDT",   "name":"Stacks",            "short":"STX"},
    {"symbol":"MINAUSDT",  "name":"Mina Protocol",     "short":"MINA"},
    {"symbol":"GMTUSDT",   "name":"STEPN",             "short":"GMT"},
]

META_MAP = {c["symbol"]: c for c in CRYPTO_SYMBOLS}

_image_cache: Dict[str, str] = {}
_image_cache_time: float = 0
_CG_CACHE_TTL = 3600
_cg_last_call: float = 0

async def _ensure_image_cache():
    global _image_cache, _image_cache_time, _cg_last_call
    if time.time() - _image_cache_time < _CG_CACHE_TTL and _image_cache:
        return
    try:
        wait = 2.5 - (time.time() - _cg_last_call)
        if wait > 0:
            await asyncio.sleep(wait)
        _cg_last_call = time.time()
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(
                f"{COINGECKO_BASE}/coins/markets",
                params={"vs_currency":"usd","per_page":50,"page":1,"sparkline":False}
            )
            if res.status_code == 200:
                for coin in res.json():
                    for sym, meta in META_MAP.items():
                        if coin.get("symbol","").upper() == meta["short"].upper():
                            _image_cache[sym] = coin.get("image","")
                _image_cache_time = time.time()
    except Exception:
        pass

async def get_all_crypto_tickers(page: int = 0, page_size: int = 10) -> List[Dict]:
    start = page * page_size
    batch = CRYPTO_SYMBOLS[start: start + page_size]
    if not batch:
        return []
    try:
        asyncio.create_task(_ensure_image_cache())
    except Exception:
        pass
    # Use individual calls - most reliable
    results = []
    for meta in batch:
        ticker = await get_crypto_ticker(meta["symbol"])
        if ticker:
            results.append(ticker)
    return results

async def get_crypto_ticker(symbol: str) -> Dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                f"{BINANCE_BASE}/ticker/24hr",
                params={"symbol": symbol}
            )
            d = res.json()
            if isinstance(d, dict) and "code" in d:
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
                "image":          _image_cache.get(symbol, ""),
            }
    except Exception as e:
        print(f"Binance error {symbol}: {e}")
        return None

async def get_crypto_klines(symbol: str, interval: str = "1d", limit: int = 60) -> List[Dict]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                f"{BINANCE_BASE}/klines",
                params={"symbol": symbol, "interval": interval, "limit": limit}
            )
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

