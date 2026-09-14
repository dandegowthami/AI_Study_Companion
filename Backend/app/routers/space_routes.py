from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from datetime import datetime

from app.database import spaces_col, projects_col
from app.schemas import SpaceCreate
from app.auth import get_current_user
from app.services.activity_service import log_activity
router = APIRouter()


@router.post("")
def create_space(data: SpaceCreate, user: dict = Depends(get_current_user)):
    space_id = str(uuid4())
    spaces_col.insert_one({
        "_id": space_id,
        "user_id": user["user_id"],
        "name": data.name,
        "description": data.description,
        "created_at": datetime.utcnow(),
        
    })
    log_activity(user["user_id"], "SPACE_CREATED", {"space_id": space_id})
    return {"space_id": space_id}


@router.get("")
def list_spaces(user: dict = Depends(get_current_user)):
    spaces = list(spaces_col.find({"user_id": user["user_id"]}))
    for s in spaces:
        s["project_count"] = projects_col.count_documents({"space_id": s["_id"]})
    return spaces


@router.get("/{space_id}")
def get_space_dashboard(space_id: str, user: dict = Depends(get_current_user)):
    space = spaces_col.find_one({"_id": space_id, "user_id": user["user_id"]})
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    projects = list(projects_col.find({"space_id": space_id}))
    return {"space": space, "projects": projects}