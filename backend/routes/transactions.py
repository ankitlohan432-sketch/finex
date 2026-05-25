from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.transactions import Transaction, TransactionType, TransactionStatus
from models.user import User
from middleware.auth_middleware import verify_token
from datetime import datetime
from typing import List, Optional

router = APIRouter(tags=["Transactions"])

class TransactionCreate(BaseModel):
    type: TransactionType
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    price_per_unit: Optional[float] = None
    total_amount: float
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    type: str
    status: str
    symbol: Optional[str]
    quantity: Optional[float]
    price_per_unit: Optional[float]
    total_amount: float
    created_at: datetime
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

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.user_id == current_user.id).order_by(Transaction.created_at.desc()).limit(50).all()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(tx: TransactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_tx = Transaction(
        user_id=current_user.id,
        type=tx.type,
        status=TransactionStatus.COMPLETED,
        symbol=tx.symbol,
        quantity=tx.quantity,
        price_per_unit=tx.price_per_unit,
        total_amount=tx.total_amount,
        description=tx.description,
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

@router.get("/summary/stats")
async def get_transaction_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    total = sum(t.total_amount for t in txs)
    buys = sum(t.total_amount for t in txs if str(t.type) in ('BUY', 'TransactionType.BUY'))
    return {"total_transactions": len(txs), "total_volume": total, "total_bought": buys}

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx
