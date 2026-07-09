from sqlalchemy import Column, String, DateTime
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
