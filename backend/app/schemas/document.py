from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    document_id: UUID
    status: str
    message: str
