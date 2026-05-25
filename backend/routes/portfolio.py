from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.portfolio import Portfolio
from models.user import User
from middleware.auth_middleware import verify_token
from datetime import datetime
from typing import Optional

router = APIRouter(tags=["Portfolio"])

class PortfolioResponse(BaseModel):
    id: int
    user_id: int
    total_balance: float
    invested_amount: float
    current_value: float
    profit_loss: float
    profit_loss_percentage: float
    cash_available: float
    class Config:
        from_attributes = True

def get_current_user(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_or_create_portfolio(user: User, db: Session) -> Portfolio:
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    if not portfolio:
        portfolio = Portfolio(
            user_id=user.id,
            total_balance=0.0,
            invested_amount=0.0,
            current_value=0.0,
            profit_loss=0.0,
            profit_loss_percentage=0.0,
            cash_available=0.0,
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    return portfolio

@router.get("/")
async def get_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = get_or_create_portfolio(current_user, db)
    return {
        "id": portfolio.id,
        "user_id": portfolio.user_id,
        "total_balance": portfolio.total_balance,
        "invested_amount": portfolio.invested_amount,
        "current_value": portfolio.current_value,
        "profit_loss": portfolio.profit_loss,
        "profit_loss_percentage": portfolio.profit_loss_percentage,
        "cash_available": portfolio.cash_available,
    }

@router.get("/summary")
async def get_portfolio_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = get_or_create_portfolio(current_user, db)
    return {
        "total_value": portfolio.total_balance,
        "gain_loss": portfolio.profit_loss,
        "gain_loss_pct": portfolio.profit_loss_percentage,
        "cash": portfolio.cash_available,
    }

@router.get("/overview")
async def get_portfolio_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = get_or_create_portfolio(current_user, db)
    return {"portfolio": portfolio.total_balance, "holdings": []}

@router.post("/update")
async def update_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = get_or_create_portfolio(current_user, db)
    return {"message": "Portfolio updated", "portfolio": portfolio.total_balance}
