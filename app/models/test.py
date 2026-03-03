from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from sqlalchemy.orm import relationship
from core.database import Base

class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, default="quiz")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    number_client = Column(Integer, default=0)
    time_test = Column(String, nullable=True)
    category = Column(String, nullable=True)
    complexity = Column(String, default='Легкий')

    # связи
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    scales = relationship("Scale", back_populates="test", cascade="all, delete-orphan")
    interpretation_rules = relationship("InterpretationRule", back_populates="test", cascade="all, delete-orphan")

    sessions = relationship("TestSession", back_populates="test", cascade="all, delete-orphan")