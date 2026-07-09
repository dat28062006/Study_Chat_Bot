from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.agent.rag_agent import rag_agent
from app.schemas.grade import GradeRequest, GradeResponse
from app.database import get_db
from app.models.submission import Submission

router = APIRouter(prefix="/api/grade", tags=["grade"])


@router.post("", response_model=GradeResponse)
async def grade_assignment(request: GradeRequest, db: Session = Depends(get_db)):
    try:
        feedback = await rag_agent.grade_homework(
            topic=request.topic,
            homework_content=request.homework_content
        )
        
        # Lưu vào Database
        submission = Submission(
            student_email=request.student_email,
            topic=request.topic,
            day_number=request.day_number,
            total_days=request.total_days,
            content=request.homework_content,
            feedback=feedback
        )
        db.add(submission)
        db.commit()
        
        # Kiểm tra tiến độ
        completed_days_count = db.query(func.count(func.distinct(Submission.day_number)))\
            .filter(Submission.student_email == request.student_email)\
            .scalar()
            
        is_completed = completed_days_count >= request.total_days

        return GradeResponse(feedback=feedback, is_completed=is_completed)
    except Exception as e:
        return GradeResponse(feedback=f"Lỗi khi chấm bài: {str(e)}", is_completed=False)
