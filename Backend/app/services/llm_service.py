import time
import json
from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.database import ai_logs_col
from uuid import uuid4
from datetime import datetime

client = Groq(api_key=GROQ_API_KEY)


def call_llm(prompt: str, feature: str, user_id: str = None, json_mode: bool = False) -> str:
    """
    Every AI call funnels through here. This single choke point is what
    makes observability trivial - one place to log latency, tokens,
    model, and success/failure for every AI feature in the app.
    """
    start = time.time()

    try:
        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            **kwargs,
        )
        content = response.choices[0].message.content
        usage = response.usage

        ai_logs_col.insert_one({
            "_id": str(uuid4()),
            "user_id": user_id,
            "feature": feature,
            "model": GROQ_MODEL,
            "latency_ms": int((time.time() - start) * 1000),
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "status": "success",
            "timestamp": datetime.utcnow(),
        })
        return content

    except Exception as e:
        ai_logs_col.insert_one({
            "_id": str(uuid4()),
            "user_id": user_id,
            "feature": feature,
            "model": GROQ_MODEL,
            "latency_ms": int((time.time() - start) * 1000),
            "status": "failure",
            "error": str(e),
            "timestamp": datetime.utcnow(),
        })
        raise


def parse_json_safe(raw: str) -> dict | None:
    """AI output must be validated before the app trusts it."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None