from datetime import datetime
from uuid import uuid4
from app.database import mastery_col

# correct answer -> mastery moves up toward 100, weighted by difficulty
# incorrect answer -> mastery moves down, weighted by difficulty
# This avoids the naive "wrong->easy, correct->hard" pattern by tracking
# *magnitude* of change based on difficulty, not just direction.
DIFFICULTY_WEIGHT = {"easy": 5, "medium": 10, "hard": 15}


def get_or_create_concept_mastery(project_id: str, concept_name: str) -> dict:
    record = mastery_col.find_one({"project_id": project_id, "concept": concept_name})
    if record:
        return record

    record = {
        "_id": str(uuid4()),
        "project_id": project_id,
        "concept": concept_name,
        "mastery_pct": 30,  # neutral starting point, not zero
        "history": [{"value": 30, "timestamp": datetime.utcnow()}],
        "updated_at": datetime.utcnow(),
    }
    mastery_col.insert_one(record)
    return record


def update_mastery(project_id: str, concept_name: str, correct: bool, difficulty: str):
    record = get_or_create_concept_mastery(project_id, concept_name)
    weight = DIFFICULTY_WEIGHT.get(difficulty, 10)
    delta = weight if correct else -weight

    new_value = max(0, min(100, record["mastery_pct"] + delta))

    mastery_col.update_one(
        {"_id": record["_id"]},
        {
            "$set": {"mastery_pct": new_value, "updated_at": datetime.utcnow()},
            "$push": {"history": {"value": new_value, "timestamp": datetime.utcnow()}},
        },
    )
    return new_value


def get_weak_concepts(project_id: str, threshold: int = 60) -> list[dict]:
    return list(mastery_col.find({"project_id": project_id, "mastery_pct": {"$lt": threshold}}))


def get_project_mastery(project_id: str) -> list[dict]:
    return list(mastery_col.find({"project_id": project_id}))