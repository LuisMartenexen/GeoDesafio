from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import SessionLocal, init_db

app = FastAPI(title="GeoArena API", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/users", response_model=schemas.UserRead)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, payload)


@app.post("/classrooms", response_model=schemas.ClassroomRead)
def create_classroom(payload: schemas.ClassroomCreate, db: Session = Depends(get_db)):
    return crud.create_classroom(db, payload)


@app.post("/questions", response_model=schemas.QuestionRead)
def create_question(payload: schemas.QuestionCreate, db: Session = Depends(get_db)):
    question = crud.create_question(db, payload)
    return _serialize_question(question)


@app.get("/questions", response_model=list[schemas.QuestionRead])
def list_questions(db: Session = Depends(get_db)):
    questions = crud.get_questions(db)
    return [_serialize_question(question) for question in questions]


@app.post("/questions/import")
def import_questions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Arquivo precisa ser CSV")
    content = file.file.read()
    return crud.import_questions_from_csv(db, content)


@app.post("/sessions", response_model=schemas.SessionRead)
def create_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
    return crud.create_session(db, payload)


@app.post("/sessions/{session_id}/questions")
def add_session_question(
    session_id: int,
    payload: schemas.SessionQuestionCreate,
    db: Session = Depends(get_db),
):
    return crud.add_session_question(db, session_id, payload)


@app.post("/groups", response_model=schemas.GroupRead)
def create_group(payload: schemas.GroupCreate, db: Session = Depends(get_db)):
    return crud.create_group(db, payload)


@app.post("/answers", response_model=schemas.AnswerRead)
def create_answer(payload: schemas.AnswerCreate, db: Session = Depends(get_db)):
    return crud.create_answer(db, payload)


@app.get("/sessions/{session_id}/ranking", response_model=list[schemas.RankingEntry])
def get_ranking(session_id: int, db: Session = Depends(get_db)):
    return crud.compute_ranking(db, session_id)


@app.get("/sessions/{session_id}/themes")
def get_theme_summary(session_id: int, db: Session = Depends(get_db)):
    return crud.summarize_per_theme(db, session_id)


def _serialize_question(question):
    tags = question.tags.split(",") if question.tags else []
    return schemas.QuestionRead(
        id=question.id,
        theme=question.theme,
        subtheme=question.subtheme,
        difficulty=question.difficulty,
        type=question.type,
        statement=question.statement,
        explanation=question.explanation,
        tags=tags,
        source=question.source,
        status=question.status,
        created_at=question.created_at,
        options=[
            schemas.QuestionOptionCreate(
                label=option.label,
                text=option.text,
                is_correct=option.is_correct,
            )
            for option in question.options
        ],
    )
