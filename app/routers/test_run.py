from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from typing import List
from datetime import datetime

# Импорты из твоих файлов
from core.database import get_db
from models import (
    Test, TestSession, UserAnswer, User,
    AnswerOption, Question, Scale
)
# Импортируем схемы. Обрати внимание на TestRunDetails (публичная схема)
from schemas.test_session import (
    TestSessionCreate, TestSessionOut, UserAnswerCreate
)
from schemas.test import TestRunDetails
from routers.auth import get_current_user  # Твоя зависимость для авторизации

router = APIRouter(prefix="/api/sessions", tags=["Test Run (Process)"])


# 1. ПОЛУЧЕНИЕ ДАННЫХ ДЛЯ ПРОХОЖДЕНИЯ (БЕЗ ВЕСОВ)
@router.get("/test/{test_id}", response_model=TestRunDetails)
async def get_test_for_run(test_id: int, db: AsyncSession = Depends(get_db)):
    """
    Отдает вопросы и варианты ответов.
    ВАЖНО: Pydantic-схема TestRunDetails автоматически скроет поле 'weight',
    чтобы пользователь не подсмотрел ответы в Network.
    """
    query = select(Test).options(
        selectinload(Test.questions).selectinload(Question.answers)
    ).where(Test.id == test_id)

    result = await db.execute(query)
    test = result.scalars().first()

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test


# 2. НАЧАЛО ТЕСТА (СОЗДАНИЕ СЕССИИ)
@router.post("/start", response_model=TestSessionOut)
async def start_session(
        data: TestSessionCreate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # Проверяем существование теста
    test = await db.get(Test, data.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # Создаем сессию
    new_session = TestSession(
        user_id=user.id,
        test_id=data.test_id,
        status="started"
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session


# 3. ЗАВЕРШЕНИЕ ТЕСТА И ПОДСЧЕТ (САМОЕ ВАЖНОЕ)
@router.post("/{session_id}/submit", response_model=TestSessionOut)
async def submit_answers(
        session_id: int,
        answers: List[UserAnswerCreate],
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 1. Загружаем сессию
    query = select(TestSession).where(TestSession.id == session_id)
    result = await db.execute(query)
    session = result.scalars().first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your session")
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Already completed")

    # 2. Сохраняем ответы и собираем баллы
    # Нам нужно достать реальные веса из БД, а не верить фронтенду

    # Сначала получим все ID выбранных опций, чтобы одним запросом достать их веса
    option_ids = [a.selected_option_id for a in answers if a.selected_option_id]

    options_map = {}  # {id: weight}
    if option_ids:
        opts_res = await db.execute(select(AnswerOption).where(AnswerOption.id.in_(option_ids)))
        options = opts_res.scalars().all()
        options_map = {opt.id: opt.weight for opt in options}

    db_answers = []

    # Формируем словарь для быстрого подсчета: {question_id: earned_weight}
    calc_data = {}

    for ans in answers:
        earned_weight = 0.0
        if ans.selected_option_id:
            # Берем вес из базы!
            earned_weight = options_map.get(ans.selected_option_id, 0.0)

        # Создаем запись ответа
        new_ans = UserAnswer(
            session_id=session.id,
            question_id=ans.question_id,
            selected_option_id=ans.selected_option_id,
            answer_text=ans.answer_text,
            value=earned_weight
        )
        db_answers.append(new_ans)

        # Сохраняем для подсчета шкал
        # Если вопрос множественный, суммируем. Если нет — перезаписываем.
        if ans.question_id in calc_data:
            calc_data[ans.question_id] += earned_weight
        else:
            calc_data[ans.question_id] = earned_weight

    db.add_all(db_answers)

    # 3. ПОДСЧЕТ РЕЗУЛЬТАТОВ ПО ШКАЛАМ
    # Загружаем Тест вместе со Шкалами, Связями и Интерпретациями
    test_query = select(Test).options(
        selectinload(Test.scales).selectinload(Scale.question_links),
        selectinload(Test.scales).selectinload(Scale.interpretations)
    ).where(Test.id == session.test_id)

    t_res = await db.execute(test_query)
    test_obj = t_res.scalars().first()

    final_results = {}  # { "Экстраверсия": {score: 10, label: "Высокая"} }

    for scale in test_obj.scales:
        scale_score = 0.0

        # Проходим по всем вопросам, привязанным к этой шкале
        for link in scale.question_links:
            # Если пользователь ответил на этот вопрос, добавляем баллы
            if link.question_id in calc_data:
                scale_score += calc_data[link.question_id]

        # Ищем интерпретацию (стенайны, стены или просто диапазоны)
        interpretation_label = "Не определено"
        interpretation_desc = None

        for rule in scale.interpretations:
            if rule.min_score <= scale_score <= rule.max_score:
                interpretation_label = rule.label
                interpretation_desc = rule.description
                break

        final_results[scale.name] = {
            "score": scale_score,
            "result": interpretation_label,
            "description": interpretation_desc
        }

    # 4. Финализируем сессию
    session.status = "completed"
    session.finished_at = datetime.utcnow()
    session.results = final_results  # SQLAlchemy сама преобразует dict в JSONB

    await db.commit()
    await db.refresh(session)

    return session