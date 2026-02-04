import csv
import io
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas


def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    user = models.User(name=payload.name, email=payload.email, role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_classroom(db: Session, payload: schemas.ClassroomCreate) -> models.Classroom:
    classroom = models.Classroom(name=payload.name, code=payload.code)
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return classroom


def create_question(db: Session, payload: schemas.QuestionCreate) -> models.Question:
    tags = ",".join(payload.tags) if payload.tags else None
    question = models.Question(
        theme=payload.theme,
        subtheme=payload.subtheme,
        difficulty=payload.difficulty,
        type=payload.type,
        statement=payload.statement,
        explanation=payload.explanation,
        tags=tags,
        source=payload.source,
        status=payload.status,
    )
    for option in payload.options:
        question.options.append(
            models.QuestionOption(
                label=option.label,
                text=option.text,
                is_correct=option.is_correct,
            )
        )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_questions(db: Session) -> list[models.Question]:
    return list(db.execute(select(models.Question)).scalars().all())


def create_session(db: Session, payload: schemas.SessionCreate) -> models.Session:
    session = models.Session(
        classroom_id=payload.classroom_id,
        name=payload.name,
        duration_minutes=payload.duration_minutes,
        time_per_question=payload.time_per_question,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def add_session_question(
    db: Session, session_id: int, payload: schemas.SessionQuestionCreate
) -> models.SessionQuestion:
    session_question = models.SessionQuestion(
        session_id=session_id,
        question_id=payload.question_id,
        order_index=payload.order_index,
    )
    db.add(session_question)
    db.commit()
    db.refresh(session_question)
    return session_question


def create_group(db: Session, payload: schemas.GroupCreate) -> models.Group:
    group = models.Group(session_id=payload.session_id, name=payload.name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def create_answer(db: Session, payload: schemas.AnswerCreate) -> models.Answer:
    option = None
    is_correct = False
    if payload.selected_option_id:
        option = db.get(models.QuestionOption, payload.selected_option_id)
        is_correct = option.is_correct if option else False
    answer = models.Answer(
        session_id=payload.session_id,
        question_id=payload.question_id,
        group_id=payload.group_id,
        user_id=payload.user_id,
        selected_option_id=payload.selected_option_id,
        is_correct=is_correct,
        elapsed_seconds=payload.elapsed_seconds,
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


def compute_ranking(db: Session, session_id: int) -> list[schemas.RankingEntry]:
    answers = list(
        db.execute(
            select(
                models.Answer.group_id,
                models.Answer.user_id,
                func.count(models.Answer.id),
                func.sum(func.case((models.Answer.is_correct == True, 1), else_=0)),
                func.avg(models.Answer.elapsed_seconds),
            ).where(models.Answer.session_id == session_id)
            .group_by(models.Answer.group_id, models.Answer.user_id)
        ).all()
    )
    entries: list[schemas.RankingEntry] = []
    for group_id, user_id, total_answers, correct_answers, avg_time in answers:
        correct_answers = correct_answers or 0
        total_points = correct_answers * 100
        avg_time = float(avg_time or 0)
        entries.append(
            schemas.RankingEntry(
                group_id=group_id,
                user_id=user_id,
                total_points=total_points,
                correct_answers=correct_answers,
                avg_time_seconds=avg_time,
            )
        )
    return entries


def import_questions_from_csv(db: Session, content: bytes) -> dict:
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    created = 0
    duplicates = []
    for row in reader:
        statement = row.get("statement", "").strip()
        if not statement:
            continue
        existing = db.execute(
            select(models.Question).where(models.Question.statement.ilike(statement))
        ).scalar_one_or_none()
        if existing:
            duplicates.append(statement)
            continue
        question = models.Question(
            theme=row.get("theme", "Geral"),
            subtheme=row.get("subtheme") or None,
            difficulty=int(row.get("difficulty", 1)),
            type=row.get("type", "multiple_choice"),
            statement=statement,
            explanation=row.get("explanation", ""),
            tags=row.get("tags") or None,
            source=row.get("source") or None,
            status=row.get("status", "draft"),
        )
        db.add(question)
        created += 1
    db.commit()
    return {"created": created, "duplicates": duplicates}


def summarize_per_theme(db: Session, session_id: int) -> dict[str, dict[str, int]]:
    rows = db.execute(
        select(models.Question.theme, models.Answer.is_correct)
        .join(models.Answer, models.Answer.question_id == models.Question.id)
        .where(models.Answer.session_id == session_id)
    ).all()
    summary: dict[str, dict[str, int]] = defaultdict(lambda: {"correct": 0, "wrong": 0})
    for theme, is_correct in rows:
        key = "correct" if is_correct else "wrong"
        summary[theme][key] += 1
    return summary
