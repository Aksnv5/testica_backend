from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from core.database import Base

class TestSession(Base):
    """
    Хранит факт прохождения теста конкретным пользователем.
    Сюда же запишем итоговый результат, чтобы не пересчитывать его каждый раз.
    """
    __tablename__ = "test_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))

    # Статус: started, completed, abandoned
    status = Column(String, default="started", index=True)

    # Тайминги
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Кэш результатов.
    # Пример: {"scales": {"extroversion": 8, "neuroticism": 2}, "verdict": "Сангвиник"}
    results = Column(JSON, nullable=True)

    # Связи
    user = relationship("User", back_populates="sessions")
    test = relationship("Test", back_populates="sessions")
    answers = relationship("UserAnswer", back_populates="session", cascade="all, delete-orphan")


class UserAnswer(Base):
    """
    Конкретный ответ пользователя на конкретный вопрос внутри сессии.
    """
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))

    # Если это выбор из вариантов (radio/checkbox)
    selected_option_id = Column(Integer, ForeignKey("answer_options.id"), nullable=True)

    # Если это открытый вопрос (text input)
    answer_text = Column(String, nullable=True)

    # Сохраняем "вес" ответа в момент сохранения.
    # Это упрощает аналитику и защищает от изменения весов в админке задним числом.
    value = Column(Float, default=0)

    # Связи
    session = relationship("TestSession", back_populates="answers")
    question = relationship("Question")
    selected_option = relationship("AnswerOption")