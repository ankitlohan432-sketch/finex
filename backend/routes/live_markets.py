"""
FINEX - Live Markets Routes
Endpoints for Crypto (Binance), NSE, BSE
"""
from fastapi import APIRouter, Query
from services.crypto_market_service import (
    get_crypto_ticker, get_crypto_klines, get_all_crypto_tickers, CRYPTO_SYMBOLS
)
from services.india_market_service import (
    get_nse_quote, get_bse_quote,
    get_nse_klines, get_bse_klines,
    get_all_nse, get_all_bse,
    get_india_indices,
    NSE_STOCKS, BSE_STOCKS
)

router = APIRouter(tags=["Live Markets"])

# ── Crypto (Binance) ──────────────────────────────────────────────────────────

@router.get("/crypto/list")
async def list_crypto():
    """Return all supported crypto symbols."""
    return CRYPTO_SYMBOLS

@router.get("/crypto/tickers")
async def crypto_tickers(page: int = Query(0, ge=0), page_size: int = Query(10, ge=1, le=30)):
    """Paginated live Binance tickers. page=0 → first 10, page=1 → next 10, etc."""
    return await get_all_crypto_tickers(page=page, page_size=page_size)

@router.get("/crypto/ticker/{binance_symbol}")
async def crypto_ticker(binance_symbol: str):
    """Single crypto ticker e.g. BTCUSDT"""
    return await get_crypto_ticker(binance_symbol.upper())

@router.get("/crypto/klines/{binance_symbol}")
async def crypto_klines(
    binance_symbol: str,
    interval: str = Query("1d", regex="^(1m|5m|15m|1h|4h|1d|1w)$"),
    limit: int = Query(60, ge=10, le=200)
):
    """OHLCV candles from Binance. interval: 1m 5m 15m 1h 4h 1d 1w"""
    return await get_crypto_klines(binance_symbol.upper(), interval=interval, limit=limit)

# ── NSE ───────────────────────────────────────────────────────────────────────

@router.get("/nse/list")
async def list_nse():
    return NSE_STOCKS

@router.get("/nse/tickers")
async def nse_tickers(page: int = Query(0, ge=0), page_size: int = Query(10, ge=1, le=30)):
    return await get_all_nse(page=page, page_size=page_size)

@router.get("/nse/ticker/{symbol}")
async def nse_ticker(symbol: str):
    return await get_nse_quote(symbol.upper())

@router.get("/nse/klines/{symbol}")
async def nse_klines(
    symbol: str,
    interval: str = Query("1d", regex="^(1h|1d|1wk)$"),
):
    return await get_nse_klines(symbol.upper(), interval=interval)

@router.get("/nse/indices")
async def nse_indices():
    return await get_india_indices()

# ── BSE ───────────────────────────────────────────────────────────────────────

@router.get("/bse/list")
async def list_bse():
    return BSE_STOCKS

@router.get("/bse/tickers")
async def bse_tickers(page: int = Query(0, ge=0), page_size: int = Query(10, ge=1, le=30)):
    return await get_all_bse(page=page, page_size=page_size)

@router.get("/bse/ticker/{symbol}")
async def bse_ticker(symbol: str):
    return await get_bse_quote(symbol.upper())

@router.get("/bse/klines/{symbol}")
async def bse_klines(
    symbol: str,
    interval: str = Query("1d", regex="^(1h|1d|1wk)$"),
):
    return await get_bse_klines(symbol.upper(), interval=interval)