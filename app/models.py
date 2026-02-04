from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    memberships = relationship("Membership", back_populates="user")
    answers = relationship("Answer", back_populates="user")


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    memberships = relationship("Membership", back_populates="classroom")
    sessions = relationship("Session", back_populates="classroom")


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "classroom_id", name="uq_membership"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)

    user = relationship("User", back_populates="memberships")
    classroom = relationship("Classroom", back_populates="memberships")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    theme: Mapped[str] = mapped_column(String(80), nullable=False)
    subtheme: Mapped[str | None] = mapped_column(String(120))
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[str | None] = mapped_column(String(200))
    source: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    session_items = relationship("SessionQuestion", back_populates="question")

    __table_args__ = (
        CheckConstraint("difficulty >= 1 AND difficulty <= 5", name="ck_question_difficulty"),
    )


class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(8), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    question = relationship("Question", back_populates="options")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=20)
    time_per_question: Mapped[int] = mapped_column(Integer, default=30)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    classroom = relationship("Classroom", back_populates="sessions")
    groups = relationship("Group", back_populates="session")
    questions = relationship("SessionQuestion", back_populates="session", cascade="all, delete-orphan")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)

    session = relationship("Session", back_populates="groups")
    answers = relationship("Answer", back_populates="group")


class SessionQuestion(Base):
    __tablename__ = "session_questions"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_session_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    session = relationship("Session", back_populates="questions")
    question = relationship("Question", back_populates="session_items")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    selected_option_id: Mapped[int | None] = mapped_column(ForeignKey("question_options.id"))
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="answers")
    user = relationship("User", back_populates="answers")
