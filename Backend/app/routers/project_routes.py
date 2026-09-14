from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from datetime import datetime

from app.database import projects_col, spaces_col, materials_col, mastery_col
from app.schemas import ProjectCreate
from app.auth import get_current_user
from app.services.activity_service import log_activity
router = APIRouter()


@router.post("")
def create_project(data: ProjectCreate, user: dict = Depends(get_current_user)):
    space = spaces_col.find_one({"_id": data.space_id, "user_id": user["user_id"]})
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    project_id = str(uuid4())
    projects_col.insert_one({
        "_id": project_id,
        "space_id": data.space_id,
        "user_id": user["user_id"],
        "name": data.name,
        "description": data.description,
        "goal": data.goal,
        "created_at": datetime.utcnow(),
        "last_accessed": datetime.utcnow(),
    })
    log_activity(user["user_id"], "PROJECT_CREATED", {"project_id": project_id})
    return {"project_id": project_id}


@router.get("/{project_id}")
def get_project_dashboard(project_id: str, user: dict = Depends(get_current_user)):
    project = projects_col.find_one({"_id": project_id, "user_id": user["user_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    projects_col.update_one({"_id": project_id}, {"$set": {"last_accessed": datetime.utcnow()}})

    materials = list(materials_col.find({"project_id": project_id}))
    mastery = list(mastery_col.find({"project_id": project_id}))
    overall_mastery = round(sum(m["mastery_pct"] for m in mastery) / len(mastery), 1) if mastery else 0

    return {
        "project": project,
        "materials": materials,
        "mastery": mastery,
        "overall_mastery": overall_mastery,
    }