import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email = Column(String, ForeignKey("users.email"), index=True, nullable=False)
    role = Column(String, nullable=False) # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
