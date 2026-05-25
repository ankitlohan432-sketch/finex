"""
FINEX - Indian Stock Market Service (NSE + BSE)
Uses NSE India open API + Yahoo Finance as fallback (no key needed)
"""
import httpx
from typing import Dict, List

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}

# NSE Nifty 50 + popular stocks
NSE_STOCKS = [
    {"symbol": "RELIANCE",    "name": "Reliance Industries",    "sector": "Energy"},
    {"symbol": "TCS",         "name": "Tata Consultancy Svcs",  "sector": "IT"},
    {"symbol": "HDFCBANK",    "name": "HDFC Bank",              "sector": "Banking"},
    {"symbol": "INFY",        "name": "Infosys",                "sector": "IT"},
    {"symbol": "ICICIBANK",   "name": "ICICI Bank",             "sector": "Banking"},
    {"symbol": "HINDUNILVR",  "name": "Hindustan Unilever",     "sector": "FMCG"},
    {"symbol": "SBIN",        "name": "State Bank of India",    "sector": "Banking"},
    {"symbol": "BAJFINANCE",  "name": "Bajaj Finance",          "sector": "Finance"},
    {"symbol": "KOTAKBANK",   "name": "Kotak Mahindra Bank",    "sector": "Banking"},
    {"symbol": "WIPRO",       "name": "Wipro",                  "sector": "IT"},
    {"symbol": "LT",          "name": "Larsen & Toubro",        "sector": "Infrastructure"},
    {"symbol": "AXISBANK",    "name": "Axis Bank",              "sector": "Banking"},
    {"symbol": "MARUTI",      "name": "Maruti Suzuki",          "sector": "Auto"},
    {"symbol": "TATAMOTORS",  "name": "Tata Motors",            "sector": "Auto"},
    {"symbol": "ADANIENT",    "name": "Adani Enterprises",      "sector": "Conglomerate"},
    {"symbol": "BHARTIARTL",  "name": "Bharti Airtel",          "sector": "Telecom"},
    {"symbol": "SUNPHARMA",   "name": "Sun Pharmaceutical",     "sector": "Pharma"},
    {"symbol": "TITAN",       "name": "Titan Company",          "sector": "Consumer"},
    {"symbol": "ASIANPAINT",  "name": "Asian Paints",           "sector": "Consumer"},
    {"symbol": "HCLTECH",     "name": "HCL Technologies",       "sector": "IT"},
    {"symbol": "ULTRACEMCO",  "name": "UltraTech Cement",       "sector": "Materials"},
    {"symbol": "NESTLEIND",   "name": "Nestle India",           "sector": "FMCG"},
    {"symbol": "POWERGRID",   "name": "Power Grid Corp",        "sector": "Utilities"},
    {"symbol": "NTPC",        "name": "NTPC",                   "sector": "Utilities"},
    {"symbol": "ONGC",        "name": "Oil & Natural Gas Corp", "sector": "Energy"},
    {"symbol": "DRREDDY",     "name": "Dr Reddy's Lab",         "sector": "Pharma"},
    {"symbol": "CIPLA",       "name": "Cipla",                  "sector": "Pharma"},
    {"symbol": "DIVISLAB",    "name": "Divi's Laboratories",    "sector": "Pharma"},
    {"symbol": "BAJAJFINSV",  "name": "Bajaj Finserv",          "sector": "Finance"},
    {"symbol": "TECHM",       "name": "Tech Mahindra",          "sector": "IT"},
]

BSE_STOCKS = [
    {"symbol": "500325",  "name": "Reliance Industries",   "ticker": "RELIANCE.BO"},
    {"symbol": "532540",  "name": "Tata Consultancy Svcs", "ticker": "TCS.BO"},
    {"symbol": "500180",  "name": "HDFC Bank",             "ticker": "HDFCBANK.BO"},
    {"symbol": "500209",  "name": "Infosys",               "ticker": "INFY.BO"},
    {"symbol": "532174",  "name": "ICICI Bank",            "ticker": "ICICIBANK.BO"},
    {"symbol": "500696",  "name": "Hindustan Unilever",    "ticker": "HINDUNILVR.BO"},
    {"symbol": "500112",  "name": "State Bank of India",   "ticker": "SBIN.BO"},
    {"symbol": "500034",  "name": "Bajaj Finance",         "ticker": "BAJFINANCE.BO"},
    {"symbol": "500247",  "name": "Kotak Mahindra Bank",   "ticker": "KOTAKBANK.BO"},
    {"symbol": "507685",  "name": "Wipro",                 "ticker": "WIPRO.BO"},
]


async def _yahoo_quote(ticker: str) -> Dict:
    """Fetch quote from Yahoo Finance (free, no key)."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    try:
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "Mozilla/5.0"}) as client:
            res = await client.get(url, params={"interval": "1d", "range": "1d"})
            d = res.json()
            meta = d.get("chart", {}).get("result", [{}])[0].get("meta", {})
            if not meta:
                return None
            price = meta.get("regularMarketPrice", 0)
            prev  = meta.get("previousClose", price)
            chg   = price - prev
            chg_p = (chg / prev * 100) if prev else 0
            return {
                "price":          round(float(price), 2),
                "change":         round(float(chg), 2),
                "change_percent": round(float(chg_p), 2),
                "high":           float(meta.get("regularMarketDayHigh", 0)),
                "low":            float(meta.get("regularMarketDayLow",  0)),
                "open":           float(meta.get("regularMarketOpen", 0)),
                "volume":         int(meta.get("regularMarketVolume", 0)),
                "currency":       meta.get("currency", "INR"),
                "exchange":       meta.get("exchangeName", ""),
            }
    except Exception as e:
        print(f"Yahoo quote error {ticker}: {e}")
        return None


async def _yahoo_klines(ticker: str, interval: str = "1d", limit: int = 60) -> List[Dict]:
    """Fetch OHLCV from Yahoo Finance."""
    range_map = {"1d": "3mo", "1h": "5d", "1wk": "1y"}
    yrange = range_map.get(interval, "3mo")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    try:
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "Mozilla/5.0"}) as client:
            res = await client.get(url, params={"interval": interval, "range": yrange})
            d   = res.json()
            result = d.get("chart", {}).get("result", [{}])[0]
            timestamps = result.get("timestamp", [])
            ohlcv = result.get("indicators", {}).get("quote", [{}])[0]
            out = []
            for i, ts in enumerate(timestamps):
                try:
                    out.append({
                        "time":   ts,
                        "open":   round(float(ohlcv["open"][i]  or 0), 2),
                        "high":   round(float(ohlcv["high"][i]  or 0), 2),
                        "low":    round(float(ohlcv["low"][i]   or 0), 2),
                        "close":  round(float(ohlcv["close"][i] or 0), 2),
                        "volume": int(ohlcv.get("volume", [0])[i] or 0),
                    })
                except (TypeError, IndexError):
                    continue
            return out[-limit:]
    except Exception as e:
        print(f"Yahoo klines error {ticker}: {e}")
        return []


async def get_nse_quote(symbol: str) -> Dict:
    meta = next((x for x in NSE_STOCKS if x["symbol"] == symbol), {"symbol": symbol, "name": symbol, "sector": ""})
    ticker = f"{symbol}.NS"
    q = await _yahoo_quote(ticker)
    if not q:
        return {"symbol": symbol, "name": meta["name"], "price": 0, "change": 0, "change_percent": 0, "exchange": "NSE", "currency": "INR"}
    return {**q, "symbol": symbol, "name": meta["name"], "sector": meta.get("sector",""), "exchange": "NSE", "currency": "INR"}


async def get_bse_quote(symbol: str) -> Dict:
    meta = next((x for x in BSE_STOCKS if x["symbol"] == symbol), {"symbol": symbol, "name": symbol, "ticker": f"{symbol}.BO"})
    q = await _yahoo_quote(meta["ticker"])
    if not q:
        return {"symbol": symbol, "name": meta["name"], "price": 0, "change": 0, "change_percent": 0, "exchange": "BSE", "currency": "INR"}
    return {**q, "symbol": symbol, "name": meta["name"], "exchange": "BSE", "currency": "INR"}


async def get_nse_klines(symbol: str, interval: str = "1d") -> List[Dict]:
    return await _yahoo_klines(f"{symbol}.NS", interval=interval, limit=90)


async def get_bse_klines(symbol: str, interval: str = "1d") -> List[Dict]:
    meta = next((x for x in BSE_STOCKS if x["symbol"] == symbol), None)
    ticker = meta["ticker"] if meta else f"{symbol}.BO"
    return await _yahoo_klines(ticker, interval=interval, limit=90)


async def get_all_nse(page: int = 0, page_size: int = 10) -> List[Dict]:
    start = page * page_size
    batch = NSE_STOCKS[start: start + page_size]
    results = []
    for meta in batch:
        q = await get_nse_quote(meta["symbol"])
        if q:
            results.append(q)
    return results


async def get_all_bse(page: int = 0, page_size: int = 10) -> List[Dict]:
    start = page * page_size
    batch = BSE_STOCKS[start: start + page_size]
    results = []
    for meta in batch:
        q = await get_bse_quote(meta["symbol"])
        if q:
            results.append(q)
    return results


async def get_india_indices() -> List[Dict]:
    """Fetch live NSE/BSE indices via Yahoo Finance."""
    indices_map = [
        {"ticker": "^NSEI",   "name": "NIFTY 50"},
        {"ticker": "^BSESN",  "name": "SENSEX"},
        {"ticker": "^NSEBANK","name": "BANK NIFTY"},
        {"ticker": "^CRSLDX", "name": "NIFTY IT"},
    ]
    out = []
    for idx in indices_map:
        q = await _yahoo_quote(idx["ticker"])
        if q:
            out.append({"name": idx["name"], **q})
    return out

