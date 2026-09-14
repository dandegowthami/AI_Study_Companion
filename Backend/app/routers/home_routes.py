from fastapi import APIRouter, Depends
from app.database import spaces_col, projects_col, mastery_col
from app.auth import get_current_user
from app.services.growth_service import get_latest_recommendation

router = APIRouter()


@router.get("")
def home_dashboard(user: dict = Depends(get_current_user)):
    uid = user["user_id"]

    recent_projects = list(
        projects_col.find({"user_id": uid}).sort("last_accessed", -1).limit(5)
    )

    project_ids = [p["_id"] for p in projects_col.find({"user_id": uid})]
    mastery_records = list(mastery_col.find({"project_id": {"$in": project_ids}}))
    overall_progress = (
        round(sum(m["mastery_pct"] for m in mastery_records) / len(mastery_records), 1)
        if mastery_records else 0
    )

    weak_concepts = list(
        mastery_col.find({"project_id": {"$in": project_ids}, "mastery_pct": {"$lt": 50}})
        .sort("mastery_pct", 1)
        .limit(5)
    )

    recommendation = None
    if recent_projects:
        recommendation = get_latest_recommendation(recent_projects[0]["_id"])

    return {
        "continue_learning": recent_projects[0] if recent_projects else None,
        "recent_projects": recent_projects,
        "overall_progress": overall_progress,
        "areas_to_improve": weak_concepts,
        "recommended_next_step": recommendation,
        "total_spaces": spaces_col.count_documents({"user_id": uid}),
        "total_projects": len(project_ids),
    }