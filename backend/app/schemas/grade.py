from pydantic import BaseModel

class GradeRequest(BaseModel):
    student_email: str
    topic: str
    day_number: int
    total_days: int
    homework_content: str

class GradeResponse(BaseModel):
    feedback: str
    is_completed: bool = False
