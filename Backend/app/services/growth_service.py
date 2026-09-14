from app.database import mastery_col, recommendations_col
from app.services.llm_service import call_llm
from uuid import uuid4
from datetime import datetime

RECOMMENDATION_PROMPT = """A student is working on a project with this learning progress:

{summary}

In 1-2 short sentences, tell them what to focus on next. Be specific and encouraging,
not generic. Reference the actual concept names given above."""


def get_growth_trends(project_id: str) -> list[dict]:
    """
    Compares each concept's earliest recorded mastery vs its current value
    to classify it as Improving / Stable / Needs Attention.
    """
    records = list(mastery_col.find({"project_id": project_id}))
    trends = []

    for r in records:
        history = r.get("history", [])
        if len(history) < 2:
            trend = "Not enough data yet"
            previous = r["mastery_pct"]
        else:
            previous = history[0]["value"]
            current = history[-1]["value"]
            change = current - previous
            if change >= 10:
                trend = "Improving"
            elif change <= -10:
                trend = "Needs Attention"
            else:
                trend = "Stable"

        trends.append({
            "concept": r["concept"],
            "previous_mastery": previous,
            "current_mastery": r["mastery_pct"],
            "trend": trend,
        })

    return trends


def generate_recommendation(project_id: str) -> str:
    trends = get_growth_trends(project_id)
    if not trends:
        return "Upload some material and take a quiz to get your first recommendation."

    summary_lines = [
        f"- {t['concept']}: {t['previous_mastery']}% -> {t['current_mastery']}% ({t['trend']})"
        for t in trends
    ]
    summary = "\n".join(summary_lines)

    recommendation = call_llm(
        RECOMMENDATION_PROMPT.format(summary=summary), feature="recommendation"
    )

    recommendations_col.insert_one({
        "_id": str(uuid4()),
        "project_id": project_id,
        "text": recommendation,
        "created_at": datetime.utcnow(),
    })

    return recommendation


def get_latest_recommendation(project_id: str) -> str | None:
    rec = recommendations_col.find_one(
        {"project_id": project_id}, sort=[("created_at", -1)]
    )
    return rec["text"] if rec else None