from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base

# --- Связующая таблица между шкалами и вопросами ---
class ScaleQuestionLink(Base):
    __tablename__ = "scale_question_links"

    id = Column(Integer, primary_key=True, index=True)
    scale_id = Column(Integer, ForeignKey("scales.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))

    scale = relationship("Scale", back_populates="question_links")
    question = relationship("Question", back_populates="scale_links")

class Scale(Base):
    __tablename__ = "scales"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    test = relationship("Test", back_populates="scales")
    # questions = relationship("Question", secondary="scale_question_links", back_populates="scales")
    interpretations = relationship("ScaleInterpretation", back_populates="scale", cascade="all, delete-orphan")
    question_links = relationship("ScaleQuestionLink", back_populates="scale", cascade="all, delete-orphan")
