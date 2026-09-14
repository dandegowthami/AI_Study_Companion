from uuid import uuid4
from datetime import datetime
from app.database import activity_col


def log_activity(user_id: str, event_type: str, metadata: dict = None):
    """
    Central place every meaningful event gets written.
    New event types = just call this with a new string, no schema change needed.
    """
    activity_col.insert_one({
        "_id": str(uuid4()),
        "user_id": user_id,
        "event_type": event_type,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow(),
    })