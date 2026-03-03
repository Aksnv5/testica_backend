from pydantic import BaseModel
from typing import Optional


# Базовая схема
class AnswerOptionBase(BaseModel):
    text: str
    category: Optional[str] = None


# Схема для СОЗДАНИЯ (Админ шлет это)
class AnswerOptionCreate(AnswerOptionBase):
    weight: float = 0
    question_id: Optional[int] = None  # Иногда нужно при создании


# Схема для ЧТЕНИЯ АДМИНОМ (Видит веса)
class AnswerOptionOut(AnswerOptionBase):
    id: int
    weight: float
    question_id: int

    class Config:
        orm_mode = True


# --- НОВАЯ СХЕМА ---
# Схема для ПРОХОЖДЕНИЯ ТЕСТА (Юзер НЕ видит веса)
class AnswerOptionPublic(BaseModel):
    id: int
    text: str

    # weight удален намеренно!

    class Config:
        orm_mode = True