from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from datetime import datetime

from app.database import quiz_attempts_col, projects_col
from app.schemas import QuizStart, QuizAnswer
from app.auth import get_current_user
from app.services.quiz_service import generate_question, evaluate_answer
from app.services.mastery_service import update_mastery
from app.services.activity_service import log_activity
from app.services.growth_service import generate_recommendation
router = APIRouter()


def _public_question(q: dict) -> dict:
    """Strip the answer key before sending a question to the client."""
    public = {k: v for k, v in q.items() if k != "correct_answer"}
    return public

QUIZ_LENGTH = 5  # questions per quiz session
@router.post("/start")
def start_quiz(data: QuizStart, user: dict = Depends(get_current_user)):
    project = projects_col.find_one({"_id": data.project_id, "user_id": user["user_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    question = generate_question(data.project_id)
    question["question_id"] = str(uuid4())

    attempt_id = str(uuid4())
    quiz_attempts_col.insert_one({
        "_id": attempt_id,
        "project_id": data.project_id,
        "user_id": user["user_id"],
        "status": "in_progress",
        "current_question": question,
        "history": [],
        "score": {"correct": 0, "total": 0},
        "started_at": datetime.utcnow(),
    })
    log_activity(user["user_id"], "QUIZ_STARTED", {"project_id": data.project_id})
    return {"quiz_attempt_id": attempt_id, "question": _public_question(question)}


@router.post("/answer")
def answer_quiz(data: QuizAnswer, user: dict = Depends(get_current_user)):
    attempt = quiz_attempts_col.find_one({"_id": data.quiz_attempt_id, "user_id": user["user_id"]})
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")

    current = attempt["current_question"]
    if current["question_id"] != data.question_id:
        raise HTTPException(status_code=400, detail="This is not the current question")

    result = evaluate_answer(current, data.answer)

    updated_mastery = update_mastery(
        attempt["project_id"], current["concept"], result["correct"], current["difficulty"]
    )

    new_score = {
        "correct": attempt["score"]["correct"] + (1 if result["correct"] else 0),
        "total": attempt["score"]["total"] + 1,
    }

    history_entry = {
        "question_text": current["question_text"],
        "concept": current["concept"],
        "student_answer": data.answer,
        "correct": result["correct"],
        "feedback": result["feedback"],
    }

    # --- Quiz completion check ---
    if new_score["total"] >= QUIZ_LENGTH:
        quiz_attempts_col.update_one(
            {"_id": data.quiz_attempt_id},
            {
                "$set": {"status": "completed", "score": new_score, "completed_at": datetime.utcnow()},
                "$push": {"history": history_entry},
            },
        )
        log_activity(user["user_id"], "QUIZ_COMPLETED", {"project_id": attempt["project_id"], "score": new_score})

        # Auto-generate recommendation now that the quiz is done (PRD section 33 workflow)
        recommendation = generate_recommendation(attempt["project_id"])

        return {
            "correct": result["correct"],
            "feedback": result["feedback"],
            "missing_concepts": result.get("missing_concepts", []),
            "updated_mastery": updated_mastery,
            "score": new_score,
            "quiz_completed": True,
            "recommendation": recommendation,
            "next_question": None,
        }

    # --- Otherwise, continue to next question ---
    next_question = generate_question(attempt["project_id"])
    next_question["question_id"] = str(uuid4())

    quiz_attempts_col.update_one(
        {"_id": data.quiz_attempt_id},
        {
            "$set": {"current_question": next_question, "score": new_score},
            "$push": {"history": history_entry},
        },
    )

    log_activity(user["user_id"], "QUESTION_ANSWERED", {"project_id": attempt["project_id"], "correct": result["correct"]})

    return {
        "correct": result["correct"],
        "feedback": result["feedback"],
        "missing_concepts": result.get("missing_concepts", []),
        "updated_mastery": updated_mastery,
        "score": new_score,
        "quiz_completed": False,
        "next_question": _public_question(next_question),
    }
@router.get("/{attempt_id}")
def get_quiz_attempt(attempt_id: str, user: dict = Depends(get_current_user)):
    attempt = quiz_attempts_col.find_one({"_id": attempt_id, "user_id": user["user_id"]})
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    attempt["current_question"] = _public_question(attempt["current_question"])
    return attempt

@router.get("/attempts/{project_id}")
def list_quiz_attempts(project_id: str, user: dict = Depends(get_current_user)):
    attempts = list(
        quiz_attempts_col.find({"project_id": project_id, "user_id": user["user_id"]})
        .sort("started_at", -1)
    )
    for a in attempts:
        a["current_question"] = None  # don't leak answer keys via this list view
    return attempts