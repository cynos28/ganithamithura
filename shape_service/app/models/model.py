from pydantic import BaseModel, Field, ConfigDict
from typing import List

class Answer(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    question_id: str = Field(..., alias="shape_id")
    answer: str = Field(..., alias="selected_word")
    
class GameAnswer(BaseModel):
    level: int
    answers: List[Answer]

class UserBadgeInfo(BaseModel):
    username: str
    badge: str

class UserBadgeList(BaseModel):
    users: List[UserBadgeInfo]