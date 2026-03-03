from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)
    order = Column(Integer, nullable=True)
    multiple = Column(Boolean, default=False)

    test = relationship("Test", back_populates="questions")
    answers = relationship("AnswerOption", back_populates="question", cascade="all, delete-orphan")
    scale_links = relationship("ScaleQuestionLink", back_populates="question", cascade="all, delete-orphan")
