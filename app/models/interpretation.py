from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from core.database import Base

# class ResultInterpretation(Base):
#     __tablename__ = "result_interpretations"
#
#     id = Column(Integer, primary_key=True, index=True)
#     scale_id = Column(Integer, ForeignKey("test_scales.id", ondelete="CASCADE"))
#     category = Column(String, nullable=True)
#     min_score = Column(Float)
#     max_score = Column(Float)
#     title = Column(String)
#     description = Column(Text)
#     recommendations = Column(Text)
#
#     # связь
#     scale = relationship("TestScale", back_populates="interpretations")
