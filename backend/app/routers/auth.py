from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.auth import LoginRequest, LoginResponse
from app.models.user import User
from app.database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        return LoginResponse(email=email, message="Tạo tài khoản mới thành công")
        
    return LoginResponse(email=email, message="Đăng nhập thành công")
