# from sqlalchemy import Column, Integer, Float, ForeignKey, JSON, DateTime
# from datetime import datetime
# from core.database import Base
#
# class Result(Base):
#     __tablename__ = "results"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, nullable=True)
#     test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
#     total_score = Column(Float)
#     result_data = Column(JSON)
#     interpretation_id = Column(Integer, ForeignKey("result_interpretations.id"))
#     created_at = Column(DateTime, default=datetime.utcnow)
