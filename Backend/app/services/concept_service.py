from app.services.llm_service import call_llm, parse_json_safe
from app.services.mastery_service import get_or_create_concept_mastery
from app.database import concepts_col
from uuid import uuid4
from datetime import datetime

CONCEPT_EXTRACTION_PROMPT = """Read the study material excerpt below and identify the 4-6 main
concepts a student would need to understand from it. Keep each concept name short (2-5 words).

Material excerpt:
{text}

Return ONLY valid JSON in this exact format, nothing else:
{{"concepts": ["Concept A", "Concept B", "Concept C"]}}"""


def extract_and_store_concepts(project_id: str, material_id: str, sample_text: str, user_id: str) -> list[str]:
    """
    Called once after a material finishes processing.
    Seeds a mastery record (starting at 30%) for each new concept so the
    Quiz and Tutor have something concrete to work with immediately.
    """
    prompt = CONCEPT_EXTRACTION_PROMPT.format(text=sample_text[:3000])
    raw = call_llm(prompt, feature="concept_extraction", user_id=user_id, json_mode=True)
    parsed = parse_json_safe(raw)

    concept_names = parsed.get("concepts", []) if parsed else []
    if not concept_names:
        concept_names = ["General Concepts"]

    for name in concept_names:
        concepts_col.update_one(
            {"project_id": project_id, "name": name},
            {"$setOnInsert": {
                "_id": str(uuid4()), "project_id": project_id, "name": name,
                "source_material_id": material_id, "created_at": datetime.utcnow(),
            }},
            upsert=True,
        )
        get_or_create_concept_mastery(project_id, name)

    return concept_names