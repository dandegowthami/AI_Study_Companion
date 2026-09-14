from pydantic import BaseModel, EmailStr
from typing import Optional


# ---------- Auth ----------
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    name: str
    role: str


# ---------- Spaces ----------
class SpaceCreate(BaseModel):
    name: str
    description: Optional[str] = ""


# ---------- Projects ----------
class ProjectCreate(BaseModel):
    space_id: str
    name: str
    description: Optional[str] = ""
    goal: str


# ---------- Tutor ----------
class TutorAsk(BaseModel):
    project_id: str
    conversation_id: Optional[str] = None
    question: str


# ---------- Quiz ----------
class QuizStart(BaseModel):
    project_id: str


class QuizAnswer(BaseModel):
    quiz_attempt_id: str
    question_id: str
    answer: str