import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from uuid import uuid4
from datetime import datetime

from app.database import materials_col, projects_col
from app.auth import get_current_user
from app.config import UPLOAD_DIR
from app.services.pdf_service import extract_text_by_page, chunk_pages
from app.services.vector_service import add_chunks
from app.services.concept_service import extract_and_store_concepts
from app.services.activity_service import log_activity

router = APIRouter()
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_material(material_id: str, project_id: str, file_path: str, material_name: str, user_id: str):
    try:
        materials_col.update_one({"_id": material_id}, {"$set": {"status": "processing"}})

        pages = extract_text_by_page(file_path)
        chunks = chunk_pages(pages)

        if not chunks:
            raise ValueError("No extractable text found in PDF")

        add_chunks(project_id, material_id, material_name, chunks)

        sample_text = " ".join(c["text"] for c in chunks[:5])
        concepts = extract_and_store_concepts(project_id, material_id, sample_text, user_id)

        materials_col.update_one(
            {"_id": material_id},
            {"$set": {
                "status": "ready", "chunk_count": len(chunks),
                "concepts": concepts, "processed_at": datetime.utcnow(),
            }},
        )
        log_activity(user_id, "MATERIAL_PROCESSING_COMPLETED", {"material_id": material_id, "project_id": project_id, "concepts": concepts})

    except Exception as e:
        materials_col.update_one(
            {"_id": material_id},
            {"$set": {"status": "failed", "error": str(e)}},
        )
        log_activity(user_id, "MATERIAL_PROCESSING_FAILED", {"material_id": material_id, "project_id": project_id, "error": str(e)})


@router.post("/upload")
def upload_material(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    project = projects_col.find_one({"_id": project_id, "user_id": user["user_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    material_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{material_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    materials_col.insert_one({
        "_id": material_id,
        "project_id": project_id,
        "name": file.filename,
        "status": "queued",
        "uploaded_at": datetime.utcnow(),
    })
    log_activity(user["user_id"], "MATERIAL_UPLOADED", {"material_id": material_id, "project_id": project_id})

    background_tasks.add_task(process_material, material_id, project_id, file_path, file.filename, user["user_id"])

    return {"material_id": material_id, "status": "queued"}


@router.get("/{material_id}/status")
def get_status(material_id: str, user: dict = Depends(get_current_user)):
    material = materials_col.find_one({"_id": material_id})
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"status": material["status"], "error": material.get("error")}