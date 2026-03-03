from pydantic import BaseModel, EmailStr, Field

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    grade: int = Field(ge=1, le=4)

class UserLogin(BaseModel):
    email: EmailStr
    password: str
