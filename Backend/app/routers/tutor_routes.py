from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from datetime import datetime

from app.database import projects_col, conversations_col, messages_col
from app.schemas import TutorAsk
from app.auth import get_current_user
from app.services.vector_service import search
from app.services.llm_service import call_llm
from app.services.context_service import get_relevant_context_summary
from app.services.activity_service import log_activity
router = APIRouter()

# If the closest retrieved chunk is farther than this, treat the question
# as unsupported rather than let the LLM guess an answer.
RELEVANCE_THRESHOLD = 1.2
TUTOR_PROMPT = """You are a study tutor. Answer the student's question using ONLY the context below.
If the context does not contain enough information to answer, say exactly:
"I don't have enough information in your materials to answer that confidently."

{learner_note}

Context:
{context}

Question: {question}

Answer clearly and simply. Do not use outside knowledge beyond the context."""


@router.post("/ask")
def ask_tutor(data: TutorAsk, user: dict = Depends(get_current_user)):
    project = projects_col.find_one({"_id": data.project_id, "user_id": user["user_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    hits = search(data.project_id, data.question, top_k=4)

    if not hits or hits[0]["distance"] > RELEVANCE_THRESHOLD:
        answer = "I don't have enough information in your materials to answer that confidently."
        sources = []
    else:
        context = "\n\n".join(f"[{h['material_name']} - Page {h['page']}]\n{h['text']}" for h in hits)
        learner_note = get_relevant_context_summary(data.project_id)
        prompt = TUTOR_PROMPT.format(context=context, question=data.question, learner_note=learner_note)
        answer = call_llm(prompt, feature="tutor", user_id=user["user_id"])
        sources = [{"material_name": h["material_name"], "page": h["page"]} for h in hits]

    conversation_id = data.conversation_id
    if not conversation_id:
        conversation_id = str(uuid4())
        conversations_col.insert_one({
            "_id": conversation_id, "project_id": data.project_id, "created_at": datetime.utcnow()
        })

    messages_col.insert_one({
        "_id": str(uuid4()), "conversation_id": conversation_id,
        "question": data.question, "answer": answer, "sources": sources,
        "timestamp": datetime.utcnow(),
    })
    log_activity(user["user_id"], "TUTOR_QUESTION_ASKED", {"project_id": data.project_id})
    return {"conversation_id": conversation_id, "answer": answer, "sources": sources}
@router.get("/conversations/{project_id}")
def get_conversations(project_id: str, user: dict = Depends(get_current_user)):
    project = projects_col.find_one({"_id": project_id, "user_id": user["user_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    convs = list(conversations_col.find({"project_id": project_id}))
    for c in convs:
        c["messages"] = list(messages_col.find({"conversation_id": c["_id"]}))
    return convs