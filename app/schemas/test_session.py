from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Any


# --- Входящие данные (от Фронта) ---

class UserAnswerCreate(BaseModel):
    question_id: int
    # Может быть ID варианта (для квиза) или текст (для открытого вопроса)
    selected_option_id: Optional[int] = None
    answer_text: Optional[str] = None


class TestSessionCreate(BaseModel):
    test_id: int


# --- Исходящие данные (на Фронт) ---

class TestSessionOut(BaseModel):
    id: int
    status: str
    created_at: datetime
    finished_at: Optional[datetime] = None

    # Результат может быть словарем или строкой, зависит от логики
    results: Optional[Any] = None

    class Config:
        orm_mode = True