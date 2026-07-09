import json
from uuid import UUID

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from app.agent.rag_agent import rag_agent
from app.schemas.chat import ChatRequest
from app.database import get_db
from app.models.chat_history import ChatHistory

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    if request.email and request.messages:
        # Lưu câu hỏi của user
        user_msg = request.messages[-1]
        if user_msg.role == "user":
            db.add(ChatHistory(
                user_email=request.email.strip().lower(),
                role="user",
                content=user_msg.content
            ))
            db.commit()

    async def event_generator():
        try:
            full_answer = ""
            async for token in rag_agent.answer(request.messages, request.document_ids, request.agent_type):
                full_answer += token
                yield {"event": "message", "data": json.dumps({"token": token})}
                
            if request.email:
                db.add(ChatHistory(
                    user_email=request.email.strip().lower(),
                    role="assistant",
                    content=full_answer
                ))
                db.commit()
                
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())
