from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.cards import Card
from models.user import User
from middleware.auth_middleware import verify_token
from typing import List
from datetime import datetime

router = APIRouter(tags=["Cards"])

class CardCreate(BaseModel):
    card_number: str
    card_holder: str
    expiry_month: int
    expiry_year: int
    card_type: str
    is_primary: bool = False

class CardResponse(BaseModel):
    id: int
    card_holder: str
    last_four: str
    card_type: str
    expiry_month: int
    expiry_year: int
    is_primary: bool
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

def get_user_from_token(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[CardResponse])
async def get_cards(current_user: User = Depends(get_user_from_token), db: Session = Depends(get_db)):
    return db.query(Card).filter(Card.user_id == current_user.id, Card.is_active == True).all()

@router.post("/", response_model=CardResponse)
async def add_card(card: CardCreate, current_user: User = Depends(get_user_from_token), db: Session = Depends(get_db)):
    db_card = Card(
        user_id=current_user.id,
        card_number=card.card_number,
        card_holder=card.card_holder,
        expiry_month=card.expiry_month,
        expiry_year=card.expiry_year,
        card_type=card.card_type,
        last_four=card.card_number[-4:],
        is_primary=card.is_primary
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@router.delete("/{card_id}")
async def delete_card(card_id: int, current_user: User = Depends(get_user_from_token), db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    card.is_active = False
    db.commit()
    return {"message": "Card removed"}
