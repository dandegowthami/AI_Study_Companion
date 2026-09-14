from fastapi import APIRouter, Depends, HTTPException
from app.database import projects_col
from app.auth import get_current_user
from app.services.growth_service import get_growth_trends, generate_recommendation, get_latest_recommendation
from app.database import activity_col, quiz_attempts_col, mastery_col, conversations_col, ai_logs_col

router = APIRouter()


@router.get("/{project_id}/growth")
def growth(project_id: str, user: dict = Depends(get_current_user)):
    project = projects_col.find_one({"_id": project_id, "user_id": user["user_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"trends": get_growth_trends(project_id)}


@router.post("/{project_id}/recommendation")
def new_recommendation(project_id: str, user: dict = Depends(get_current_user)):
    project = projects_col.find_one({"_id": project_id, "user_id": user["user_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    text = generate_recommendation(project_id)
    return {"recommendation": text}


@router.get("/{project_id}/recommendation")
def latest_recommendation(project_id: str, user: dict = Depends(get_current_user)):
    project = projects_col.find_one({"_id": project_id, "user_id": user["user_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    text = get_latest_recommendation(project_id)
    return {"recommendation": text}


@router.get("/{project_id}/overview")
def project_analytics(project_id: str, user: dict = Depends(get_current_user)):
    project = projects_col.find_one({"_id": project_id, "user_id": user["user_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # --- Activity ---
    tutor_questions = activity_col.count_documents(
        {"user_id": user["user_id"], "event_type": "TUTOR_QUESTION_ASKED", "metadata.project_id": project_id}
    )
    quiz_attempts = list(quiz_attempts_col.find({"project_id": project_id}))
    questions_answered = sum(a["score"]["total"] for a in quiz_attempts)

    # --- Performance ---
    total_correct = sum(a["score"]["correct"] for a in quiz_attempts)
    accuracy = round((total_correct / questions_answered) * 100, 1) if questions_answered else 0

    mastery_records = list(mastery_col.find({"project_id": project_id}))
    overall_mastery = (
        round(sum(m["mastery_pct"] for m in mastery_records) / len(mastery_records), 1)
        if mastery_records else 0
    )
    concepts_mastered = sum(1 for m in mastery_records if m["mastery_pct"] >= 80)
    concepts_needing_attention = sum(1 for m in mastery_records if m["mastery_pct"] < 50)

    # --- AI Activity ---
    ai_calls = list(ai_logs_col.find({"user_id": user["user_id"]}))
    project_ai_calls = [c for c in ai_calls if c.get("feature") in
                         ("tutor", "quiz_generation", "quiz_grading", "concept_extraction", "recommendation")]

    return {
        "activity": {
            "tutor_questions": tutor_questions,
            "quiz_attempts": len(quiz_attempts),
            "questions_answered": questions_answered,
        },
        "performance": {
            "quiz_accuracy_pct": accuracy,
            "overall_mastery_pct": overall_mastery,
            "concepts_mastered": concepts_mastered,
            "concepts_needing_attention": concepts_needing_attention,
        },
        "ai_activity": {
            "total_ai_calls": len(project_ai_calls),
            "successful": sum(1 for c in project_ai_calls if c["status"] == "success"),
            "failed": sum(1 for c in project_ai_calls if c["status"] == "failure"),
        },
    }
    
from app.database import spaces_col


@router.get("/global/overview")
def global_analytics(user: dict = Depends(get_current_user)):
    uid = user["user_id"]

    all_projects = list(projects_col.find({"user_id": uid}))
    project_ids = [p["_id"] for p in all_projects]

    # --- Overall Learning ---
    total_spaces = spaces_col.count_documents({"user_id": uid})
    total_projects = len(all_projects)

    activity_events = list(activity_col.find({"user_id": uid}))
    active_days = len({e["timestamp"].date() for e in activity_events})

    # --- Learning Performance ---
    mastery_records = list(mastery_col.find({"project_id": {"$in": project_ids}}))
    overall_mastery = (
        round(sum(m["mastery_pct"] for m in mastery_records) / len(mastery_records), 1)
        if mastery_records else 0
    )
    concepts_improving = sum(1 for m in mastery_records if len(m.get("history", [])) >= 2
                              and m["history"][-1]["value"] - m["history"][0]["value"] >= 10)
    concepts_needing_attention = sum(1 for m in mastery_records if m["mastery_pct"] < 50)

    quiz_attempts = list(quiz_attempts_col.find({"project_id": {"$in": project_ids}}))
    total_answered = sum(a["score"]["total"] for a in quiz_attempts)
    total_correct = sum(a["score"]["correct"] for a in quiz_attempts)
    avg_accuracy = round((total_correct / total_answered) * 100, 1) if total_answered else 0

    # --- AI Usage ---
    ai_calls = list(ai_logs_col.find({"user_id": uid}))
    tutor_calls = sum(1 for c in ai_calls if c.get("feature") == "tutor")
    quiz_gen_calls = sum(1 for c in ai_calls if c.get("feature") == "quiz_generation")

    return {
        "overall_learning": {
            "total_spaces": total_spaces,
            "total_projects": total_projects,
            "active_days": active_days,
            "total_activity_events": len(activity_events),
        },
        "learning_performance": {
            "overall_mastery_pct": overall_mastery,
            "avg_quiz_accuracy_pct": avg_accuracy,
            "concepts_improving": concepts_improving,
            "concepts_needing_attention": concepts_needing_attention,
        },
        "ai_usage": {
            "total_ai_requests": len(ai_calls),
            "tutor_interactions": tutor_calls,
            "quiz_questions_generated": quiz_gen_calls,
        },
    }