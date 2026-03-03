# --- Комбинированная интерпретация (многомерные тесты) ---
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from core.database import Base

class InterpretationRule(Base):
    __tablename__ = "interpretation_rules"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Условия, например:
    # [
    #   {"scale": "Экстраверсия", "min": 5, "max": 10},
    #   {"scale": "Нейротизм", "min": 0, "max": 4}
    # ]
    conditions = Column(JSON, nullable=False)

    test = relationship("Test", back_populates="interpretation_rules")