from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging
import time
from datetime import datetime

from config import settings
from database import engine, SessionLocal, Base

# Import all models so tables get created
import models.user
import models.admin
import models.analytics
import models.cards
import models.portfolio
import models.transactions

from routes import auth, users, stocks, portfolio, transactions, analytics, admin, chatbot, cards

# ML/DL Module - separate prediction features
from ml_dl.routes.ml_routes import router as ml_router

# Live Markets: Crypto (Binance), NSE, BSE
from routes.live_markets import router as live_markets_router

# AI Predictions: ML + DL for all markets
from routes.predictions import router as predictions_router

# Admin Control Panel (SECRET - only for ankitlohan432@gmail.com)
from routes.admin_control import router as admin_control_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create all tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FINEX Backend Starting...")
    yield
    logger.info("FINEX Backend Shutting down...")

app = FastAPI(
    title="FINEX",
    version="1.0.0",
    description="Fintech platform API",
    lifespan=lifespan
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    return response

# Core Routes
app.include_router(auth.router,         prefix="/auth",         tags=["Auth"])
app.include_router(users.router,        prefix="/users",        tags=["Users"])
app.include_router(stocks.router,       prefix="/stocks",       tags=["Stocks"])
app.include_router(portfolio.router,    prefix="/portfolio",    tags=["Portfolio"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(analytics.router,    prefix="/analytics",    tags=["Analytics"])
app.include_router(admin.router,        prefix="/admin",        tags=["Admin"])
app.include_router(chatbot.router,      prefix="/chat",         tags=["Chat"])
app.include_router(cards.router,        prefix="/cards",        tags=["Cards"])

# ML/DL Prediction endpoints
app.include_router(ml_router,           prefix="/ml",           tags=["ML Predictions"])

# Live Market Data: Crypto (Binance), NSE, BSE
app.include_router(live_markets_router, prefix="/live",         tags=["Live Markets"])

# AI Predictions: ML + DL Ensemble
app.include_router(predictions_router,  prefix="/predict",      tags=["AI Predictions"])

# Admin Control Panel (SECRET - hidden from regular users)
app.include_router(admin_control_router, prefix="",             tags=["Admin Control (SECRET)"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/ready")
async def readiness_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"ready": True}
    except Exception as e:
        return JSONResponse(status_code=503, content={"ready": False, "error": str(e)})

@app.get("/")
async def root():
    return {"message": "FINEX API", "docs": "/docs"}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
