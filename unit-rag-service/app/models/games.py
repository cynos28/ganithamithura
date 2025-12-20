from beanie import Document
from typing import Dict, Optional
from datetime import datetime
from pydantic import Field

class GameParameters(Document):
    domain: str = Field(...)
    params: Dict

    class Settings:
        name = "game_parameters"


class GameSession(Document):
    user_id: Optional[str]
    domain: str
    attempts: int
    time_spent: float
    target_time: float
    hints_used: int
    diagnosis: Optional[str]
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "game_sessions"
