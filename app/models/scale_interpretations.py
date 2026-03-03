# --- Комбинированная интерпретация (многомерные тесты) ---
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, Float
)
from sqlalchemy.orm import relationship
from core.database import Base

# --- Интерпретация внутри шкалы ---
class ScaleInterpretation(Base):
    __tablename__ = "scale_interpretations"

    id = Column(Integer, primary_key=True, index=True)
    scale_id = Column(Integer, ForeignKey("scales.id", ondelete="CASCADE"))
    min_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    label = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    scale = relationship("Scale", back_populates="interpretations")