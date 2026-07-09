from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.models.chat_history import ChatHistory
from app.database import get_db

router = APIRouter(prefix="/api/chat", tags=["history"])

class HistoryResponseItem(BaseModel):
    role: str
    content: str
    
    class Config:
        from_attributes = True

@router.get("/history/{email}", response_model=List[HistoryResponseItem])
def get_history(email: str, db: Session = Depends(get_db)):
    email = email.strip().lower()
    history = db.query(ChatHistory).filter(ChatHistory.user_email == email).order_by(ChatHistory.created_at.asc()).all()
    return history
