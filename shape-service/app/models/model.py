from pydantic import BaseModel, Field
from typing import List

class UserCreate(BaseModel):
    username: str
    password: str

class Answer(BaseModel):
    question_id: str = Field(..., alias="shape_id")
    answer: str = Field(..., alias="selected_word")
    
class GameAnswer(BaseModel):
    level: int
    answers: List[Answer]