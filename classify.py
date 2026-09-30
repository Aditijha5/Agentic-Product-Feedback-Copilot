"""Step 1: classifier agent. Labels each review with category, sentiment, severity, topic."""
import pandas as pd

from .config import CATEGORIES, PROMPTS
from .llm import call_llm, parse_json

# Keyword rules used ONLY in --mock mode so the pipeline can run without an API key.
# They are not a meaningful baseline; never report mock-mode accuracy as a result.
_KEYWORDS = [
    ("bug", ["crash", "bug", "error", "freeze", "frozen", "stuck", "not working", "doesn't work",
             "won't", "fails", "glitch", "broken", "logged out"]),
    ("performance", ["slow", "lag", "loading", "battery", "takes forever", "drain", "delay"]),
    ("pricing", ["price", "expensive", "subscription", "charged", "refund", "fee", "costly", "paid plan"]),
    ("feature_request", ["please add", "wish", "would love", "should have", "missing", "add a",
                         "need a", "option to", "support for"]),
    ("ux", ["confusing", "hard to find", "layout", "navigate", "navigation", "cluttered", "interface"]),
    ("praise", ["love", "great", "awesome", "excellent", "perfect", "amazing", "best app"]),
]


def _heuristic(text: str, rating: int) -> dict:
    t = text.lower()
    category, topic = "other", "general"
    for cat, words in _KEYWORDS:
        hit = next((w for w in words if w in t), None)
        if hit:
            category, topic = cat, hit
            break
    sentiment = "negative" if rating <= 2 else "neutral" if rating == 3 else "positive"
    severity = 1 if category == "praise" else {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}[rating]
    return {"category": category, "sentiment": sentiment, "severity": severity, "topic": topic}


def load_prompt(version: str) -> str:
    return (PROMPTS / f"classifier_{version}.txt").read_text()


def _call_batch(system: str, payload: list) -> list:
    import json

    user = "Classify these reviews. Return ONLY a JSON list.\n" + json.dumps(payload, ensure_ascii=False)
    last_err = None
    for _ in range(2):  # one retry on malformed JSON
        try:
            result = parse_json(call_llm(system, user))
            if isinstance(result, list):
                return result
        except Exception as e:  # noqa: BLE001
            last_err = e
    raise RuntimeError(f"Classifier returned unparseable output twice: {last_err}")


def classify_reviews(df: pd.DataFrame, version: str = "v2", mock: bool = False, batch_size: int = 10) -> pd.DataFrame:
    rows = []
    if mock:
        for r in df.itertuples():
            rows.append({"review_id": r.review_id, **_heuristic(r.text, r.rating)})
    else:
        system = load_prompt(version)
        for i in range(0, len(df), batch_size):
            chunk = df.iloc[i : i + batch_size]
            payload = [{"id": str(r.review_id), "text": r.text, "rating": int(r.rating)} for r in chunk.itertuples()]
            by_id = {str(x.get("id")): x for x in _call_batch(system, payload)}
            for r in chunk.itertuples():
                x = by_id.get(str(r.review_id), {})
                cat = x.get("category")
                sev = x.get("severity", 3)
                rows.append(
                    {
                        "review_id": r.review_id,
                        "category": cat if cat in CATEGORIES else "other",
                        "sentiment": x.get("sentiment", "neutral"),
                        "severity": min(5, max(1, int(sev))) if str(sev).isdigit() else 3,
                        "topic": str(x.get("topic", "general")).lower()[:60],
                    }
                )
    return df.merge(pd.DataFrame(rows), on="review_id", how="left")
