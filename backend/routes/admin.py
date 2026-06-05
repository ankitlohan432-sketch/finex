from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.transactions import Transaction
from middleware.auth_middleware import verify_token
from datetime import datetime
from typing import List

router = APIRouter(tags=["Admin"])

def get_admin_user(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/users")
async def get_all_users(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "is_active": u.is_active, "is_admin": u.is_admin, "created_at": u.created_at.isoformat() if u.created_at else None} for u in users]

@router.get("/stats/platform")
async def get_platform_stats(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_transactions = db.query(Transaction).count()
    return {"total_users": total_users, "active_users": active_users, "total_transactions": total_transactions, "api_uptime": 99.9}

@router.post("/users/{user_id}/suspend")
async def suspend_user(user_id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user_id} suspended"}

@router.post("/users/{user_id}/activate")
async def activate_user(user_id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"message": f"User {user_id} activated"}

