from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    document_ids: list[str] | None = None
    agent_type: str = "mentor"
    email: str | None = None
