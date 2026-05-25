from fastapi import APIRouter
from services.market_service import market_service

router = APIRouter(tags=["Stocks"])

@router.get("/price/{symbol}")
async def get_stock_price(symbol: str):
    return await market_service.get_stock_price(symbol)

@router.get("/history/{symbol}")
async def get_stock_history(symbol: str, interval: str = "1day"):
    history = await market_service.get_stock_history(symbol, interval)
    return history

@router.get("/top-movers")
async def get_top_movers():
    return await market_service.get_top_movers()

@router.get("/indices")
async def get_indices():
    overview = await market_service.get_market_overview()
    return overview.get("indices", [])

@router.get("/overview")
async def get_market_overview():
    return await market_service.get_market_overview()
