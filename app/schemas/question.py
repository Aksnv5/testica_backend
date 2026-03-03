from pydantic import BaseModel
from typing import Optional, List
from .answer_option import AnswerOptionOut, AnswerOptionCreate, AnswerOptionPublic

# Схема для отдачи теста ЮЗЕРУ (безопасная)
class QuestionPublic(BaseModel):
    id: int
    text: str
    order: Optional[int] = None
    multiple: bool
    # Используем безопасную схему ответов
    answers: List[AnswerOptionPublic] = []

    class Config:
        orm_mode = True

# Схема для АДМИНКИ (полная)
class QuestionOut(BaseModel):
    id: int
    text: str
    order: Optional[int] = None
    multiple: bool
    answers: List[AnswerOptionOut] = [] # Админ видит веса

    class Config:
        orm_mode = True

class QuestionCreate(BaseModel):
    text: str
    order: Optional[int] = None
    multiple: bool = False
    answers: List[AnswerOptionCreate] = []