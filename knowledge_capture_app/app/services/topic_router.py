from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from app.models import Topic
except ModuleNotFoundError:
    from models import Topic


def route_topic(db: Session, file_type: str, text_blob: str) -> Topic | None:
    topic_candidates = db.scalars(select(Topic)).all()
    lower_blob = text_blob.lower()

    keyword_map = {
        "AI Infrastructure": ["ai", "gpu", "data center", "cloud", "backlog", "capex"],
        "Market Valuation": ["p/e", "valuation", "earnings", "multiple", "forward"],
        "ETF and Market Structure": ["etf", "index", "rebalancing", "tracking", "arbitrage"],
    }

    for topic in topic_candidates:
        for keyword in keyword_map.get(topic.name, []):
            if keyword in lower_blob:
                return topic

    if file_type == "image":
        return next((t for t in topic_candidates if t.name == "AI Infrastructure"), None)
    return topic_candidates[0] if topic_candidates else None
