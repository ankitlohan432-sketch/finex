from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from middleware.auth_middleware import verify_token
from datetime import datetime
from typing import Optional

router = APIRouter(tags=["Analytics"])

def get_current_user(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user

@router.get("/dashboard")
async def get_analytics_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    return {"total_users": total_users, "active_users": active_users, "total_transactions": 0, "api_uptime": 99.9, "fraud_attempts": 0, "fraud_blocked": 0}

@router.get("/users-growth")
async def get_users_growth(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"week": f"W{i+1}", "users": 10 + i * 5} for i in range(8)]

@router.get("/traffic-overview")
async def get_traffic_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    return [{"day": d, "visits": 100 + i * 50} for i, d in enumerate(days)]

@router.post("/log")
async def log_action(page: str, action: str, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    return {"logged": True}
