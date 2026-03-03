from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base

class AnswerOption(Base):
    __tablename__ = "answer_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    text = Column(String, nullable=False)
    weight = Column(Float, default=0)
    category = Column(String, nullable=True)

    question = relationship("Question", back_populates="answers")
