from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str
    email: str
    role: str


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ClassroomCreate(BaseModel):
    name: str
    code: str


class ClassroomRead(BaseModel):
    id: int
    name: str
    code: str
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionOptionCreate(BaseModel):
    label: str
    text: str
    is_correct: bool = False


class QuestionCreate(BaseModel):
    theme: str
    subtheme: str | None = None
    difficulty: int = Field(ge=1, le=5)
    type: str
    statement: str
    explanation: str
    tags: list[str] = []
    source: str | None = None
    status: str = "draft"
    options: list[QuestionOptionCreate] = []


class QuestionRead(BaseModel):
    id: int
    theme: str
    subtheme: str | None
    difficulty: int
    type: str
    statement: str
    explanation: str
    tags: list[str]
    source: str | None
    status: str
    created_at: datetime
    options: list[QuestionOptionCreate]

    model_config = {"from_attributes": True}


class SessionCreate(BaseModel):
    classroom_id: int
    name: str
    duration_minutes: int = 20
    time_per_question: int = 30


class SessionRead(BaseModel):
    id: int
    classroom_id: int
    name: str
    status: str
    duration_minutes: int
    time_per_question: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionQuestionCreate(BaseModel):
    question_id: int
    order_index: int


class GroupCreate(BaseModel):
    session_id: int
    name: str


class GroupRead(BaseModel):
    id: int
    session_id: int
    name: str

    model_config = {"from_attributes": True}


class AnswerCreate(BaseModel):
    session_id: int
    question_id: int
    group_id: int | None = None
    user_id: int | None = None
    selected_option_id: int | None = None
    elapsed_seconds: int = 0


class AnswerRead(BaseModel):
    id: int
    session_id: int
    question_id: int
    group_id: int | None
    user_id: int | None
    selected_option_id: int | None
    is_correct: bool
    elapsed_seconds: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RankingEntry(BaseModel):
    group_id: int | None
    user_id: int | None
    total_points: int
    correct_answers: int
    avg_time_seconds: float
