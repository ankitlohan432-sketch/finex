from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, VisitorLog
from middleware.auth_middleware import verify_token
from typing import Optional
from datetime import datetime

router = APIRouter(tags=["Users"])

def get_user_from_token(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def user_to_dict(user: User):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }

@router.get("/me")
async def get_current_user(current_user: User = Depends(get_user_from_token)):
    return user_to_dict(current_user)

@router.put("/me")
async def update_user_profile(
    full_name: Optional[str] = None,
    phone: Optional[str] = None,
    current_user: User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    if full_name:
        current_user.full_name = full_name
    if phone:
        current_user.phone = phone
    db.commit()
    return {"message": "Profile updated", "user": user_to_dict(current_user)}

@router.get("/stats")
async def get_user_stats(db: Session = Depends(get_db)):
    return {
        "total_users": db.query(User).count(),
        "verified_users": db.query(User).filter(User.is_verified == True).count(),
        "active_users": db.query(User).filter(User.is_active == True).count(),
    }
