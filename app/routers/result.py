# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from typing import List, Optional
#
# from core.database import get_db
# from models import Result
# from schemas import ResultCreate, ResultUpdate, ResultOut
#
# router = APIRouter(prefix="/results", tags=["Results"])
#
#
# @router.get("/", response_model=List[ResultOut])
# async def get_results(
#     db: AsyncSession = Depends(get_db),
#     limit: int = Query(20, ge=1, le=100),
#     offset: int = Query(0, ge=0),
#     user_id: Optional[int] = None,
#     test_id: Optional[int] = None,
# ):
#     """
#     Получить список результатов с фильтрацией и пагинацией.
#     """
#     stmt = select(Result)
#
#     if user_id:
#         stmt = stmt.filter(Result.user_id == user_id)
#     if test_id:
#         stmt = stmt.filter(Result.test_id == test_id)
#
#     stmt = stmt.offset(offset).limit(limit)
#
#     result = await db.execute(stmt)
#     results = result.scalars().all()
#     return results
#
#
# @router.get("/{result_id}", response_model=ResultOut)
# async def get_result(result_id: int, db: AsyncSession = Depends(get_db)):
#     stmt = select(Result).filter(Result.id == result_id)
#     result = await db.execute(stmt)
#     res = result.scalars().first()
#     if not res:
#         raise HTTPException(status_code=404, detail="Result not found")
#     return res
#
#
# @router.post("/", response_model=ResultOut)
# async def create_result(result_data: ResultCreate, db: AsyncSession = Depends(get_db)):
#     result = Result(**result_data.dict())
#     db.add(result)
#     await db.commit()
#     await db.refresh(result)
#     return result
#
#
# @router.put("/{result_id}", response_model=ResultOut)
# async def update_result(result_id: int, result_data: ResultUpdate, db: AsyncSession = Depends(get_db)):
#     stmt = select(Result).filter(Result.id == result_id)
#     db_result = await db.execute(stmt)
#     res = db_result.scalars().first()
#
#     if not res:
#         raise HTTPException(status_code=404, detail="Result not found")
#
#     for key, value in result_data.dict(exclude_unset=True).items():
#         setattr(res, key, value)
#
#     await db.commit()
#     await db.refresh(res)
#     return res
#
#
# @router.delete("/{result_id}")
# async def delete_result(result_id: int, db: AsyncSession = Depends(get_db)):
#     stmt = select(Result).filter(Result.id == result_id)
#     db_result = await db.execute(stmt)
#     res = db_result.scalars().first()
#
#     if not res:
#         raise HTTPException(status_code=404, detail="Result not found")
#
#     await db.delete(res)
#     await db.commit()
#     return {"message": "Result deleted successfully"}
