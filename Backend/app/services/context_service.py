from app.services.mastery_service import get_weak_concepts


def get_relevant_context_summary(project_id: str) -> str:
    """
    Selective retrieval: builds a short note with only what's relevant
    right now, instead of dumping full history into every Tutor prompt.
    """
    weak = get_weak_concepts(project_id, threshold=50)
    weak_names = [w["concept"] for w in weak]

    if not weak_names:
        return ""

    return f"Note: this student has previously struggled with: {', '.join(weak_names)}. Keep this in mind if relevant to the question."