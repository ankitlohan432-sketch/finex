from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models.user import User
from auth_utils import auth_handler
from services.mail_service import mail_service
from services.activity_tracker import activity_tracker
from config import settings
from datetime import datetime, timedelta
from typing import Optional
import asyncio
import random
import string
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])

# ── Schemas ───────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class ResendOTP(BaseModel):
    email: EmailStr

# ── Helpers ───────────────────────────────────────────────────────────────────

def generate_otp() -> str:
    """Generate a 6-digit numeric OTP"""
    return ''.join(random.choices(string.digits, k=6))

def user_to_dict(user):
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

# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register")
async def register(user_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    # Check duplicate email
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        if existing.is_verified:
            raise HTTPException(status_code=400, detail="Email already registered")
        # Unverified account: refresh OTP and resend
        otp = generate_otp()
        existing.otp_code = otp
        existing.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
        existing.otp_attempts = 0
        existing.password_hash = auth_handler.hash_password(user_data.password)
        existing.full_name = user_data.full_name
        existing.phone = user_data.phone
        db.commit()
        asyncio.create_task(mail_service.send_otp_email(existing.email, existing.full_name, otp))
        logger.info(f"🔐 DEV OTP for {existing.email}: {otp}")
        return {
            "message": "OTP resent to your email. Please verify your account.",
            "email": existing.email,
            "requires_verification": True
        }

    # Generate OTP
    otp = generate_otp()

    # Create user — NOT active/verified until OTP confirmed
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=auth_handler.hash_password(user_data.password),
        phone=user_data.phone,
        is_active=False,
        is_verified=False,
        otp_code=otp,
        otp_expires_at=datetime.utcnow() + timedelta(minutes=10),
        otp_attempts=0,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Send OTP email (non-blocking)
    asyncio.create_task(mail_service.send_otp_email(db_user.email, db_user.full_name, otp))
    logger.info(f"🔐 DEV OTP for {db_user.email}: {otp}")

    return {
        "message": "Account created! Please check your email for the 6-digit verification code.",
        "email": db_user.email,
        "requires_verification": True
    }

# ── Verify OTP ────────────────────────────────────────────────────────────────

@router.post("/verify-otp")
async def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Account not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Account already verified. Please login.")

    # Too many attempts
    if user.otp_attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many incorrect attempts. Please request a new OTP.")

    # Expired
    if not user.otp_expires_at or datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    # Wrong OTP
    if user.otp_code != data.otp.strip():
        user.otp_attempts += 1
        db.commit()
        remaining = 5 - user.otp_attempts
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect OTP. {remaining} attempt(s) remaining."
        )

    # ✅ OTP correct — activate account
    user.is_verified = True
    user.is_active = True
    user.otp_code = None
    user.otp_expires_at = None
    user.otp_attempts = 0
    db.commit()
    db.refresh(user)

    # Log registration to CSV tracker
    activity_tracker.log_registration(
        user_id=str(user.id),
        email=user.email,
        username=user.full_name,
        phone=user.phone
    )

    # Send welcome email
    asyncio.create_task(mail_service.send_welcome_email(user.email, user.full_name))

    # Return token so frontend logs them in directly
    token = auth_handler.create_access_token({"sub": str(user.id), "email": user.email})
    return {
        "message": "Email verified successfully! Welcome to Finex.",
        "access_token": token,
        "token_type": "bearer",
        "user": user_to_dict(user)
    }

# ── Resend OTP ────────────────────────────────────────────────────────────────

@router.post("/resend-otp")
async def resend_otp(data: ResendOTP, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Account not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Account already verified.")

    # Cooldown: don't allow resend if OTP is less than 1 minute old
    if user.otp_expires_at:
        time_left = user.otp_expires_at - datetime.utcnow()
        if time_left.total_seconds() > 540:  # 9 min left = sent less than 1 min ago
            raise HTTPException(status_code=429, detail="Please wait at least 1 minute before requesting a new OTP.")

    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    user.otp_attempts = 0
    db.commit()

    asyncio.create_task(mail_service.send_otp_email(user.email, user.full_name, otp))
    logger.info(f"🔐 DEV OTP for {user.email}: {otp}")

    return {"message": "New OTP sent to your email.", "email": user.email}

# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login")
async def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not auth_handler.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Not verified yet
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email first. Check your inbox for the OTP."
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive. Please contact support.")

    user.last_login = datetime.utcnow()
    db.commit()

    ip = request.client.host if request.client else "Unknown"
    asyncio.create_task(mail_service.send_login_alert(user.email, user.full_name, ip))

    activity_tracker.log_login(
        user_id=str(user.id),
        email=user.email,
        ip_address=ip,
        device=request.headers.get("User-Agent", "Unknown")
    )

    token = auth_handler.create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer", "user": user_to_dict(user)}

# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}

# ── Refresh Token ─────────────────────────────────────────────────────────────

@router.post("/refresh-token")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    try:
        _, token = request.headers.get("Authorization", "").split()
        payload = auth_handler.decode_token(token)
        user = db.query(User).filter(User.id == int(payload["sub"])).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_token = auth_handler.create_access_token({"sub": str(user.id), "email": user.email})
        return {"access_token": new_token, "token_type": "bearer", "user": user_to_dict(user)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"message": "If this email exists, a reset code has been sent."}
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    user.otp_attempts = 0
    db.commit()
    asyncio.create_task(mail_service.send_password_reset_email(user.email, user.full_name, otp))
    logger.info(f"Password reset OTP for {user.email}: {otp}")
    return {"message": "Reset code sent to your email.", "email": data.email}

@router.post("/reset-password")
async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    if user.otp_attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many attempts. Request a new code.")
    if not user.otp_expires_at or datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Reset code expired. Please request a new one.")
    if user.otp_code != data.otp:
        user.otp_attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid reset code.")
    user.password_hash = auth_handler.hash_password(data.new_password)
    user.otp_code = None
    user.otp_expires_at = None
    user.otp_attempts = 0
    db.commit()
    return {"message": "Password reset successful. Please login."}


class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"message": "If this email exists, a reset code has been sent."}
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    user.otp_attempts = 0
    db.commit()
    asyncio.create_task(mail_service.send_password_reset_email(user.email, user.full_name, otp))
    logger.info(f"Password reset OTP for {user.email}: {otp}")
    return {"message": "Reset code sent to your email.", "email": data.email}

@router.post("/reset-password")
async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    if user.otp_attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many attempts. Request a new code.")
    if not user.otp_expires_at or datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Reset code expired. Please request a new one.")
    if user.otp_code != data.otp:
        user.otp_attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid reset code.")
    user.password_hash = auth_handler.hash_password(data.new_password)
    user.otp_code = None
    user.otp_expires_at = None
    user.otp_attempts = 0
    db.commit()
    return {"message": "Password reset successful. Please login."}

class ForgotPassword(BaseModel):

    email: EmailStr

class ResetPassword(BaseModel):

    email: EmailStr

    otp: str

    new_password: str

@router.post("/forgot-password")

async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:

        return {"message": "If this email exists, a reset code has been sent."}

    otp = generate_otp()

    user.otp_code = otp

    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)

    user.otp_attempts = 0

    db.commit()

    asyncio.create_task(mail_service.send_password_reset_email(user.email, user.full_name, otp))

    logger.info(f"Password reset OTP for {user.email}: {otp}")

    return {"message": "Reset code sent to your email.", "email": data.email}

@router.post("/reset-password")

async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:

        raise HTTPException(status_code=404, detail="Account not found")

    if user.otp_attempts >= 5:

        raise HTTPException(status_code=429, detail="Too many attempts. Request a new code.")

    if not user.otp_expires_at or datetime.utcnow() > user.otp_expires_at:

        raise HTTPException(status_code=400, detail="Reset code expired. Please request a new one.")

    if user.otp_code != data.otp:

        user.otp_attempts += 1

        db.commit()

        raise HTTPException(status_code=400, detail="Invalid reset code.")

    user.password_hash = auth_handler.hash_password(data.new_password)

    user.otp_code = None

    user.otp_expires_at = None

    user.otp_attempts = 0

    db.commit()

    return {"message": "Password reset successful. Please login."}

