import time
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import (
    db, users_col, spaces_col, projects_col, materials_col, activity_col, ai_logs_col,
    quiz_attempts_col, mastery_col, recommendations_col, messages_col, eval_results_col,
)
from app.auth import require_admin
from app.services.vector_service import chroma_client

router = APIRouter()

STUCK_MATERIAL_THRESHOLD_MINUTES = 10
UNSUPPORTED_ANSWER_TEXT = "I don't have enough information in your materials to answer that confidently."

# Placeholder per-1k-token rates for a rough cost estimate only — Groq usage
# isn't billed per-token the same way across models, so this is illustrative,
# not a real billing figure.
COST_PER_1K_INPUT_TOKENS_USD = 0.00005
COST_PER_1K_OUTPUT_TOKENS_USD = 0.00008


def _user_map() -> dict:
    return {u["_id"]: {"name": u["name"], "email": u["email"]} for u in users_col.find({}, {"name": 1, "email": 1})}


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
@router.get("/overview")
def admin_overview(admin: dict = Depends(require_admin)):
    total_users = users_col.count_documents({"role": {"$ne": "admin"}})
    total_spaces = spaces_col.count_documents({})
    total_projects = projects_col.count_documents({})
    total_materials = materials_col.count_documents({})

    ai_calls = list(ai_logs_col.find({}))
    ai_errors = sum(1 for c in ai_calls if c["status"] == "failure")
    ai_error_rate = round((ai_errors / len(ai_calls)) * 100, 1) if ai_calls else 0
    avg_latency = round(sum(c.get("latency_ms", 0) for c in ai_calls) / len(ai_calls), 1) if ai_calls else 0

    return {
        "total_users": total_users,
        "total_spaces": total_spaces,
        "total_projects": total_projects,
        "total_materials": total_materials,
        "total_ai_requests": len(ai_calls),
        "ai_error_rate_pct": ai_error_rate,
        "avg_ai_latency_ms": avg_latency,
        "tutor_questions_asked": activity_col.count_documents({"event_type": "TUTOR_QUESTION_ASKED"}),
        "quiz_attempts_started": activity_col.count_documents({"event_type": "QUIZ_STARTED"}),
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
@router.get("/users")
def list_users(admin: dict = Depends(require_admin)):
    # The Admin Dashboard tracks learners, not other admin accounts.
    users = list(users_col.find({"role": {"$ne": "admin"}}, {"password_hash": 0}))
    for u in users:
        u["space_count"] = spaces_col.count_documents({"user_id": u["_id"]})
        u["project_count"] = projects_col.count_documents({"user_id": u["_id"]})
    return users


@router.get("/users/{user_id}")
def user_detail(user_id: str, admin: dict = Depends(require_admin)):
    user = users_col.find_one({"_id": user_id}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    spaces = list(spaces_col.find({"user_id": user_id}))
    projects = list(projects_col.find({"user_id": user_id}))
    project_ids = [p["_id"] for p in projects]

    quiz_attempts = list(quiz_attempts_col.find({"project_id": {"$in": project_ids}}))
    total_answered = sum(a["score"]["total"] for a in quiz_attempts)
    total_correct = sum(a["score"]["correct"] for a in quiz_attempts)
    accuracy = round((total_correct / total_answered) * 100, 1) if total_answered else 0

    activity_timeline = list(
        activity_col.find({"user_id": user_id}).sort("timestamp", -1).limit(20)
    )

    return {
        "user": user,
        "spaces_count": len(spaces),
        "projects_count": len(projects),
        "quiz_accuracy_pct": accuracy,
        "activity_timeline": activity_timeline,
    }


# ---------------------------------------------------------------------------
# Spaces & Projects
# ---------------------------------------------------------------------------
@router.get("/spaces")
def list_all_spaces(admin: dict = Depends(require_admin)):
    users = _user_map()
    spaces = list(spaces_col.find({}))

    result = []
    for s in spaces:
        projects = list(projects_col.find({"space_id": s["_id"]}))
        last_activity = s["created_at"]
        for p in projects:
            candidate = p.get("last_accessed") or p.get("created_at")
            if candidate and candidate > last_activity:
                last_activity = candidate

        result.append({
            "_id": s["_id"],
            "name": s["name"],
            "owner": users.get(s["user_id"], {"name": "Unknown", "email": ""}),
            "project_count": len(projects),
            "created_at": s["created_at"],
            "last_activity": last_activity,
        })

    result.sort(key=lambda x: x["last_activity"], reverse=True)
    return result


@router.get("/spaces/{space_id}")
def get_space_detail(space_id: str, admin: dict = Depends(require_admin)):
    space = spaces_col.find_one({"_id": space_id})
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    users = _user_map()
    projects = list(projects_col.find({"space_id": space_id}))
    for p in projects:
        p["material_count"] = materials_col.count_documents({"project_id": p["_id"]})
        mastery = list(mastery_col.find({"project_id": p["_id"]}))
        p["overall_mastery_pct"] = round(sum(m["mastery_pct"] for m in mastery) / len(mastery), 1) if mastery else 0

    return {
        "space": space,
        "owner": users.get(space["user_id"], {"name": "Unknown", "email": ""}),
        "projects": projects,
    }


@router.get("/projects")
def list_all_projects(admin: dict = Depends(require_admin)):
    users = _user_map()
    space_names = {s["_id"]: s["name"] for s in spaces_col.find({}, {"name": 1})}
    projects = list(projects_col.find({}))

    result = []
    for p in projects:
        mastery = list(mastery_col.find({"project_id": p["_id"]}))
        overall_mastery = round(sum(m["mastery_pct"] for m in mastery) / len(mastery), 1) if mastery else 0

        result.append({
            "_id": p["_id"],
            "name": p["name"],
            "owner": users.get(p["user_id"], {"name": "Unknown", "email": ""}),
            "space_name": space_names.get(p["space_id"], "Unknown"),
            "material_count": materials_col.count_documents({"project_id": p["_id"]}),
            "tutor_questions": activity_col.count_documents(
                {"event_type": "TUTOR_QUESTION_ASKED", "metadata.project_id": p["_id"]}
            ),
            "quiz_attempts": quiz_attempts_col.count_documents({"project_id": p["_id"]}),
            "overall_mastery_pct": overall_mastery,
            "last_activity": p.get("last_accessed") or p.get("created_at"),
        })

    result.sort(key=lambda x: x["last_activity"], reverse=True)
    return result


@router.get("/projects/{project_id}")
def get_project_detail(project_id: str, admin: dict = Depends(require_admin)):
    project = projects_col.find_one({"_id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    users = _user_map()
    space = spaces_col.find_one({"_id": project["space_id"]})
    materials = list(materials_col.find({"project_id": project_id}))
    mastery = list(mastery_col.find({"project_id": project_id}))
    quiz_attempts = list(quiz_attempts_col.find({"project_id": project_id}))
    activity_timeline = list(
        activity_col.find({"metadata.project_id": project_id}).sort("timestamp", -1).limit(30)
    )

    return {
        "project": project,
        "owner": users.get(project["user_id"], {"name": "Unknown", "email": ""}),
        "space_name": space["name"] if space else "Unknown",
        "materials": materials,
        "mastery": mastery,
        "quiz_attempts_count": len(quiz_attempts),
        "activity_timeline": activity_timeline,
    }


# ---------------------------------------------------------------------------
# Activity (global feed)
# ---------------------------------------------------------------------------
@router.get("/activity")
def list_activity(
    user_id: str | None = None,
    event_type: str | None = None,
    project_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = Query(50, le=200),
    skip: int = Query(0, ge=0),
    admin: dict = Depends(require_admin),
):
    query: dict = {}
    if user_id:
        query["user_id"] = user_id
    if event_type:
        query["event_type"] = event_type
    if project_id:
        query["metadata.project_id"] = project_id

    ts_query = {}
    if start_date:
        try:
            ts_query["$gte"] = datetime.fromisoformat(start_date)
        except ValueError:
            pass
    if end_date:
        try:
            ts_query["$lte"] = datetime.fromisoformat(end_date)
        except ValueError:
            pass
    if ts_query:
        query["timestamp"] = ts_query

    total = activity_col.count_documents(query)
    events = list(activity_col.find(query).sort("timestamp", -1).skip(skip).limit(limit))

    users = _user_map()
    for e in events:
        owner = users.get(e["user_id"])
        e["user_name"] = owner["name"] if owner else "Unknown"
        e["user_email"] = owner["email"] if owner else ""

    return {
        "total": total,
        "events": events,
        "event_types": sorted(activity_col.distinct("event_type")),
    }


# ---------------------------------------------------------------------------
# Learning Analytics (cross-user)
# ---------------------------------------------------------------------------
@router.get("/learning-analytics")
def learning_analytics(admin: dict = Depends(require_admin)):
    now = datetime.utcnow()
    day7 = now - timedelta(days=7)
    day30 = now - timedelta(days=30)
    day14 = now - timedelta(days=14)

    all_events = list(activity_col.find({}))
    events_7d = [e for e in all_events if e["timestamp"] >= day7]
    events_30d = [e for e in all_events if e["timestamp"] >= day30]

    daily_counts: dict = {}
    for e in all_events:
        if e["timestamp"] >= day14:
            key = e["timestamp"].strftime("%Y-%m-%d")
            daily_counts[key] = daily_counts.get(key, 0) + 1
    daily_trend = [{"date": d, "count": c} for d, c in sorted(daily_counts.items())]

    event_type_counts: dict = {}
    for e in all_events:
        event_type_counts[e["event_type"]] = event_type_counts.get(e["event_type"], 0) + 1
    frequently_used_features = sorted(
        ({"event_type": k, "count": v} for k, v in event_type_counts.items()),
        key=lambda x: x["count"], reverse=True,
    )[:8]

    quiz_attempts = list(quiz_attempts_col.find({}))
    total_answered = sum(a["score"]["total"] for a in quiz_attempts)
    total_correct = sum(a["score"]["correct"] for a in quiz_attempts)
    avg_accuracy = round((total_correct / total_answered) * 100, 1) if total_answered else 0

    mastery_records = list(mastery_col.find({}))
    overall_mastery = (
        round(sum(m["mastery_pct"] for m in mastery_records) / len(mastery_records), 1)
        if mastery_records else 0
    )

    struggling: dict = {}
    for m in mastery_records:
        if m["mastery_pct"] < 50:
            struggling[m["concept"]] = struggling.get(m["concept"], 0) + 1
    struggling_concepts = sorted(
        ({"concept": k, "learners_struggling": v} for k, v in struggling.items()),
        key=lambda x: x["learners_struggling"], reverse=True,
    )[:5]

    return {
        "learning_activity": {
            "total_events": len(all_events),
            "events_last_7_days": len(events_7d),
            "events_last_30_days": len(events_30d),
            "daily_trend": daily_trend,
        },
        "user_engagement": {
            "total_users": users_col.count_documents({"role": {"$ne": "admin"}}),
            "active_users_7d": len({e["user_id"] for e in events_7d}),
            "active_users_30d": len({e["user_id"] for e in events_30d}),
        },
        "assessment_performance": {
            "avg_quiz_accuracy_pct": avg_accuracy,
            "total_quiz_attempts": len(quiz_attempts),
            "completed_quiz_attempts": sum(1 for a in quiz_attempts if a["status"] == "completed"),
        },
        "average_mastery_pct": overall_mastery,
        "frequently_used_features": frequently_used_features,
        "struggling_concepts": struggling_concepts,
        "active_projects": {
            "total": projects_col.count_documents({}),
            "active_last_7_days": projects_col.count_documents({"last_accessed": {"$gte": day7}}),
        },
    }


# ---------------------------------------------------------------------------
# AI Usage & Evaluation
# ---------------------------------------------------------------------------
@router.get("/ai-usage")
def ai_usage(admin: dict = Depends(require_admin)):
    logs = list(ai_logs_col.find({}))

    by_feature: dict = {}
    for log in logs:
        feature = log.get("feature", "unknown")
        by_feature.setdefault(feature, {"count": 0, "failures": 0, "total_tokens": 0})
        by_feature[feature]["count"] += 1
        if log["status"] == "failure":
            by_feature[feature]["failures"] += 1
        by_feature[feature]["total_tokens"] += log.get("input_tokens", 0) + log.get("output_tokens", 0)

    total_input_tokens = sum(l.get("input_tokens", 0) for l in logs)
    total_output_tokens = sum(l.get("output_tokens", 0) for l in logs)
    estimated_cost_usd = round(
        (total_input_tokens / 1000) * COST_PER_1K_INPUT_TOKENS_USD
        + (total_output_tokens / 1000) * COST_PER_1K_OUTPUT_TOKENS_USD,
        4,
    )

    now = datetime.utcnow()
    day14 = now - timedelta(days=14)
    daily_counts: dict = {}
    for l in logs:
        if l["timestamp"] >= day14:
            key = l["timestamp"].strftime("%Y-%m-%d")
            bucket = daily_counts.setdefault(key, {"count": 0, "failures": 0})
            bucket["count"] += 1
            if l["status"] == "failure":
                bucket["failures"] += 1
    daily_trend = [{"date": d, **v} for d, v in sorted(daily_counts.items())]

    latencies = [l.get("latency_ms", 0) for l in logs]
    recent = sorted(logs, key=lambda l: l["timestamp"], reverse=True)[:10]

    return {
        "total_requests": len(logs),
        "by_feature": by_feature,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "estimated_cost_usd": estimated_cost_usd,
        "cost_note": "Rough estimate from placeholder per-1k-token rates, not actual billing data.",
        "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else 0,
        "max_latency_ms": max(latencies) if latencies else 0,
        "daily_trend": daily_trend,
        "recent_requests": recent,
    }


def _compute_evaluation() -> dict:
    """
    Heuristic AI-quality snapshot built entirely from data already logged by
    the app (tutor messages + ai_logs) rather than a fabricated score, since
    there's no human-labeled eval set yet:
      - groundedness / unsupported-question handling from tutor messages
      - structured-output reliability from ai_logs success/failure per feature
    """
    messages = list(messages_col.find({}))
    total_answers = len(messages)
    unsupported = sum(1 for m in messages if m["answer"] == UNSUPPORTED_ANSWER_TEXT)
    grounded = sum(1 for m in messages if m.get("sources"))
    avg_sources = (
        round(sum(len(m.get("sources", [])) for m in messages) / total_answers, 2)
        if total_answers else 0
    )

    logs = list(ai_logs_col.find({}))

    def failure_rate(feature: str):
        feature_logs = [l for l in logs if l.get("feature") == feature]
        if not feature_logs:
            return None
        failures = sum(1 for l in feature_logs if l["status"] == "failure")
        return round((failures / len(feature_logs)) * 100, 1)

    quiz_attempts = list(quiz_attempts_col.find({}))
    completed = [a for a in quiz_attempts if a["status"] == "completed"]

    return {
        "tutor": {
            "total_answers": total_answers,
            "groundedness_rate_pct": round((grounded / total_answers) * 100, 1) if total_answers else 0,
            "unsupported_handling_rate_pct": round((unsupported / total_answers) * 100, 1) if total_answers else 0,
            "avg_sources_per_answer": avg_sources,
            "note": (
                "Groundedness = % of answers backed by at least one retrieved source. "
                "Unsupported-handling = % of answers that correctly refused due to insufficient evidence."
            ),
        },
        "assessment": {
            "quiz_generation_failure_rate_pct": failure_rate("quiz_generation"),
            "quiz_grading_failure_rate_pct": failure_rate("quiz_grading"),
            "quiz_attempts_completed": len(completed),
            "quiz_attempts_started": len(quiz_attempts),
        },
        "recommendations": {
            "recommendation_failure_rate_pct": failure_rate("recommendation"),
            "recommendations_generated": recommendations_col.count_documents({}),
        },
        "concept_extraction": {
            "failure_rate_pct": failure_rate("concept_extraction"),
        },
    }


@router.get("/evaluation")
def evaluation_view(admin: dict = Depends(require_admin)):
    return {
        "current": _compute_evaluation(),
        "history": list(eval_results_col.find({}).sort("timestamp", -1).limit(20)),
    }


@router.post("/evaluation/snapshot")
def evaluation_snapshot(admin: dict = Depends(require_admin)):
    """Persists the current evaluation view so later snapshots can be compared for regressions (PRD §47)."""
    snapshot = _compute_evaluation()
    snapshot["_id"] = str(uuid4())
    snapshot["timestamp"] = datetime.utcnow()
    eval_results_col.insert_one(snapshot)
    return snapshot


# ---------------------------------------------------------------------------
# System Health
# ---------------------------------------------------------------------------
@router.get("/system-health")
def system_health(admin: dict = Depends(require_admin)):
    db_healthy = True
    db_latency_ms = None
    try:
        start = time.time()
        db.command("ping")
        db_latency_ms = round((time.time() - start) * 1000, 1)
    except Exception:
        db_healthy = False

    chroma_healthy = True
    try:
        chroma_client.heartbeat()
    except Exception:
        chroma_healthy = False

    material_status_counts = {
        status: materials_col.count_documents({"status": status})
        for status in ("queued", "processing", "ready", "failed")
    }
    stuck_cutoff = datetime.utcnow() - timedelta(minutes=STUCK_MATERIAL_THRESHOLD_MINUTES)
    stuck_materials = list(materials_col.find({
        "status": {"$in": ["queued", "processing"]},
        "uploaded_at": {"$lt": stuck_cutoff},
    }))

    recent_logs = list(ai_logs_col.find({}).sort("timestamp", -1).limit(50))
    recent_failures = sum(1 for l in recent_logs if l["status"] == "failure")
    recent_error_rate = round((recent_failures / len(recent_logs)) * 100, 1) if recent_logs else 0
    recent_avg_latency = (
        round(sum(l.get("latency_ms", 0) for l in recent_logs) / len(recent_logs), 1)
        if recent_logs else 0
    )

    return {
        "database": {"healthy": db_healthy, "latency_ms": db_latency_ms},
        "vector_store": {"healthy": chroma_healthy},
        "ai_provider": {
            "recent_error_rate_pct": recent_error_rate,
            "recent_avg_latency_ms": recent_avg_latency,
            "sample_size": len(recent_logs),
        },
        "background_processing": {
            "material_status_counts": material_status_counts,
            "stuck_materials_count": len(stuck_materials),
            "stuck_materials": [
                {"_id": m["_id"], "name": m["name"], "status": m["status"], "uploaded_at": m["uploaded_at"]}
                for m in stuck_materials
            ],
        },
        "recent_ai_failures": [
            {"feature": l.get("feature"), "error": l.get("error"), "timestamp": l["timestamp"]}
            for l in recent_logs if l["status"] == "failure"
        ][:10],
    }
