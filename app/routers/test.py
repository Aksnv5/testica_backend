from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select
from typing import List, Optional
from schemas import TestCreate, TestOut, TestUpdate, TestCreateWithQuestions, TestOutSmall
from core.database import get_db
from models import Test, Question, AnswerOption, ScaleInterpretation, ScaleQuestionLink, Scale

router = APIRouter(prefix="/api/tests", tags=["Tests"])


@router.get("/", response_model=List[TestOutSmall])
async def get_tests(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    complexity: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    stmt = select(Test)

    if category:
        stmt = stmt.filter(Test.category == category)
    if complexity:
        stmt = stmt.filter(Test.complexity == complexity)
    if is_active is not None:
        stmt = stmt.filter(Test.is_active == is_active)

    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    tests = result.scalars().all()
    return tests


@router.get("/{test_id}", response_model=TestOut)
async def get_test(test_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Test)
        .options(
            joinedload(Test.questions).selectinload(Question.answers)
        )
        .filter(Test.id == test_id)
    )
    test = result.scalars().first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

# @router.post("/", response_model=TestOut)
# async def create_test(test_data: TestCreate, db: AsyncSession = Depends(get_db)):
#     test = Test(**test_data.dict())
#     db.add(test)
#     await db.commit()
#     await db.refresh(test)
#     return test


@router.put("/{test_id}", response_model=TestOut)
async def update_test(test_id: int, test_data: TestUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Test).filter(Test.id == test_id)
    result = await db.execute(stmt)
    test = result.scalars().first()

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    for key, value in test_data.dict(exclude_unset=True).items():
        setattr(test, key, value)

    await db.commit()
    await db.refresh(test)
    return test


@router.delete("/{test_id}")
async def delete_test(test_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Test).filter(Test.id == test_id)
    result = await db.execute(stmt)
    test = result.scalars().first()

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    await db.delete(test)
    await db.commit()
    return {"message": "Test deleted successfully"}

@router.post('/create', status_code=201)
async def create_test(data: TestCreateWithQuestions, db: AsyncSession = Depends(get_db)):
    test = Test(
        title=data.title,
        description=data.description,
        type=data.type,
        is_active=data.is_active,
        number_client=data.number_client or 0,
        time_test=data.time_test,
        category=data.category,
        complexity=data.complexity
    )

    for q in data.questions:
        question = Question(
            text=q.text,
            order=q.order,
            multiple=q.multiple
        )
        for a in q.answers:
            answer = AnswerOption(
                text=a.text,
                weight=a.weight,
                category=a.category
            )
            question.answers.append(answer)
        test.questions.append(question)

    async with db.begin():  # ✅ безопасный commit
        db.add(test)
    # await db.refresh(test)
    return {
        "title": test.title,
        "questions_count": len(test.questions)
    }

@router.post('/create_full', status_code=201)
async def create_full_test(data: dict, db: AsyncSession = Depends(get_db)):
    """Создание теста из JSON со шкалами и интерпретациями"""
    test = Test(
        title=data["title"],
        description=data.get("description"),
        time_test=data.get("time_test"),
        category=data.get("category"),
        complexity=data.get("complexity"),
        number_client=data.get("number_client", 0),
        is_active=True
    )

    question_map = {}  # text → объект Question

    # --- Вопросы и ответы ---
    for q in data["questions"]:
        question = Question(
            text=q["text"],
            order=q.get("order", 0),
            multiple=q.get("multiple", False)
        )
        for a in q.get("answers", []):
            answer = AnswerOption(
                text=a["text"],
                weight=a.get("weight", 0),
                category=a.get("category")
            )
            question.answers.append(answer)
        test.questions.append(question)
        question_map[q["text"]] = question  # чтобы потом связать шкалы

    async with db.begin():
        db.add(test)
        await db.flush()  # ✅ чтобы появились id вопросов

        # --- Шкалы и интерпретации ---
        for scale_data in data.get("scales", []):
            scale = Scale(
                name=scale_data["name"],
                description=scale_data.get("description"),
                test_id=test.id
            )

            # Привязка вопросов по тексту
            for q_text in scale_data.get("questions", []):
                if q_text in question_map:
                    link = ScaleQuestionLink(question_id=question_map[q_text].id)
                    scale.question_links.append(link)

            # интерпретации шкалы
            for interp in scale_data.get("interpretations", []):
                si = ScaleInterpretation(
                    min_score=interp["min_score"],
                    max_score=interp["max_score"],
                    label=interp["label"],
                    description=interp.get("description"),
                    # recommendations=interp.get("recommendations")
                )
                scale.interpretations.append(si)

            db.add(scale)

    return {"message": f"Тест '{test.title}' успешно создан"}



async def calculate_test_result(test_id: int, user_answers: dict, db: AsyncSession):
    """
    user_answers: {question_id: answer_weight_or_list_of_weights}
    Возвращает: {scale_name: {"score": X, "interpretation": Y}}
    """
    result = {}
    test = await db.get(Test, test_id)

    for scale in test.scales:
        scale_score = 0
        for link in scale.question_links:
            q_id = link.question_id
            answer_weight = user_answers.get(q_id)
            if isinstance(answer_weight, list):
                scale_score += sum(answer_weight)
            elif isinstance(answer_weight, int):
                scale_score += answer_weight

        # Найти интерпретацию
        interp_label = None
        interp_description = None
        for interp in scale.interpretations:
            if interp.min_score <= scale_score <= interp.max_score:
                interp_label = interp.label
                interp_description = interp.description
                break

        result[scale.name] = {
            "score": scale_score,
            "interpretation": {
                "label": interp_label,
                "description": interp_description
            }
        }

    return result