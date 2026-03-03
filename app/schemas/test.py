from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

from .question import QuestionOut, QuestionCreate, QuestionPublic


class TestBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: Optional[str] = "quiz"
    is_active: Optional[bool] = True
    number_client: Optional[int] = None
    time_test: Optional[str] = None
    category: Optional[str] = None
    complexity: Optional[str] = None


class TestCreate(TestBase):
    title: str
    description: str
    type: str
    is_active: bool
    number_client: int
    time_test: str
    category: str
    complexity: str


class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None
    number_client: Optional[int] = None
    time_test: Optional[str] = None
    category: Optional[str] = None
    complexity: Optional[str] = None

class TestOut(TestBase):
    id: int
    created_at: datetime
    questions: List[QuestionOut] = []

    class Config:
        orm_mode = True

# --- НОВАЯ СХЕМА ---
# Для Прохождения (скрытые веса)
class TestRunDetails(TestBase):
    id: int
    questions: List[QuestionPublic] = []

    class Config:
        orm_mode = True


class TestOutSmall(TestBase):
    id: int
    created_at: datetime
    # questions: List[QuestionOut] = []

    class Config:
        orm_mode = True
class TestCreateWithQuestions(BaseModel):
    title: str
    description: Optional[str] = None
    type: Optional[str] = "quiz"
    is_active: Optional[bool] = True
    number_client: Optional[int] = 0
    time_test: Optional[str] = None
    category: Optional[str] = None
    complexity: Optional[str] = None
    questions: List[QuestionCreate] = []