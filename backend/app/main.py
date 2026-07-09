from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import chat, documents, grade, auth, history

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(grade.router)
app.include_router(auth.router)
app.include_router(history.router)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/cancel/{job_id}")
def cancel_job(job_id: str):
    from app.tools.email_tool import scheduler
    try:
        scheduler.remove_job(job_id)
        return {"message": f"Đã hủy lịch nhắc nhở thành công! (ID: {job_id})"}
    except Exception as e:
        return {"message": "Lịch nhắc nhở này đã được gửi, đã bị hủy trước đó, hoặc không tồn tại."}
