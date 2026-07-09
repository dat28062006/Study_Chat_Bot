import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_email = Column(String, index=True, nullable=False)
    topic = Column(String, nullable=False)
    day_number = Column(Integer, nullable=False)
    total_days = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
