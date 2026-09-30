"""Step 2: theme agent. Groups fine-grained topics into a small number of product themes."""
import json

import pandas as pd

from .config import DEFAULT_EFFORT_WEEKS
from .llm import call_llm, parse_json

SYSTEM = """You are a product analyst. You receive a list of short topics extracted from app reviews,
each with a count. Group them into at most {n} product themes a PM could act on.
Return ONLY JSON:
{{"themes": [{{"name": "...", "description": "one sentence", "topics": ["topic", ...], "effort_weeks": <integer estimate of person-weeks to address>}}]}}
Every topic must appear in exactly one theme. Theme names should describe the user problem, not the solution."""

PRAISE = "Praise (not actioned)"
UNSORTED = "Other / uncategorized"


def assign_themes(df: pd.DataFrame, mock: bool = False, max_themes: int = 6):
    df = df.copy()
    actionable = df["category"] != "praise"
    meta: dict = {}

    if mock:
        for cat in df.loc[actionable, "category"].unique():
            name = cat.replace("_", " ").title()
            meta[name] = {"description": f"Reviews categorized as {cat}.", "effort_weeks": DEFAULT_EFFORT_WEEKS.get(cat, 3)}
        df["theme"] = df["category"].map(lambda c: c.replace("_", " ").title())
    else:
        counts = df.loc[actionable, "topic"].value_counts().head(150)
        payload = [{"topic": t, "count": int(c)} for t, c in counts.items()]
        raw = call_llm(SYSTEM.format(n=max_themes), json.dumps(payload), max_tokens=3000)
        themes = parse_json(raw)["themes"]
        topic_to_theme = {}
        for th in themes:
            meta[th["name"]] = {"description": th.get("description", ""), "effort_weeks": max(1, int(th.get("effort_weeks", 4)))}
            for t in th.get("topics", []):
                topic_to_theme[t] = th["name"]
        df["theme"] = df["topic"].map(topic_to_theme).fillna(UNSORTED)
        if (df.loc[actionable, "theme"] == UNSORTED).any():
            meta[UNSORTED] = {"description": "Topics the theme agent did not group.", "effort_weeks": 3}

    df.loc[~actionable, "theme"] = PRAISE
    return df, meta
