# from datetime import datetime
# from typing import Optional, Any
# from pydantic import BaseModel
#
#
# class ResultBase(BaseModel):
#     user_id: Optional[int] = None
#     test_id: int
#     total_score: Optional[float] = None
#     result_data: Optional[Any] = None
#     interpretation_id: Optional[int] = None
#
#
# class ResultCreate(ResultBase):
#     user_id: Optional[int] = None
#     test_id: int
#     total_score: float
#     result_data: Any
#     interpretation_id: Optional[int] = None
#
#
# class ResultUpdate(BaseModel):
#     total_score: Optional[float] = None
#     result_data: Optional[Any] = None
#     interpretation_id: Optional[int] = None
#
#
# class ResultOut(ResultBase):
#     id: int
#     created_at: datetime
#
#     class Config:
#         orm_mode = True
