from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, UploadResponse
from app.services.embedding_service import embedding_service
from app.services.pdf_service import pdf_service
from app.services.s3_service import s3_service
from app.services.vector_service import vector_service

router = APIRouter(prefix="/api/documents", tags=["documents"])


def process_document(document_id: str, s3_key: str, db_url: str):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        doc.status = "processing"
        db.commit()

        text = pdf_service.extract_text(s3_key)
        chunks = pdf_service.chunk_text(
            text,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        embeddings = embedding_service.embed_batch(chunks)
        vector_service.upsert(str(document_id), chunks, embeddings)

        doc.status = "indexed"
        doc.chunk_count = len(chunks)
        db.commit()

    except Exception as e:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = "failed"
            doc.error_message = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chi chap nhan file PDF")

    s3_key = await s3_service.upload(file)

    doc = Document(
        filename=file.filename,
        s3_key=s3_key,
        status="uploading",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(
        process_document,
        str(doc.id),
        s3_key,
        settings.database_url,
    )

    return UploadResponse(
        document_id=doc.id,
        status="processing",
        message="File da upload, dang xu ly indexing...",
    )


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: UUID, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document khong ton tai")
    return doc


@router.delete("/{document_id}")
def delete_document(document_id: UUID, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document khong ton tai")

    vector_service.delete_by_document(str(document_id))
    db.delete(doc)
    db.commit()
    return {"message": "Da xoa document"}
