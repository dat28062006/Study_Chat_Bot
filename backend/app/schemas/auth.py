from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str

class LoginResponse(BaseModel):
    email: str
    message: str
