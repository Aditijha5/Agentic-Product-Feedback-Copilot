"""Step 4: PRD agent. Drafts a PRD for each top-ranked theme."""
import re

import pandas as pd

from .config import OUT
from .llm import call_llm

SYSTEM = """You are a senior product manager. Write a concise PRD in Markdown for the theme below, using ONLY the
evidence provided (review quotes and stats). Sections: Problem Statement, Evidence, Target Users, User Stories
(3, format 'As a..., I want..., so that...'), Proposed Solution (high level), Acceptance Criteria (4 bullets),
Success Metrics (2-3 measurable), Risks & Open Questions. Do not invent statistics. Keep under 450 words."""


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def draft_prds(df: pd.DataFrame, ranked: pd.DataFrame, top_n: int = 3, mock: bool = False) -> dict:
    out_dir = OUT / "prds"
    out_dir.mkdir(parents=True, exist_ok=True)
    prds = {}
    for row in ranked.head(top_n).itertuples():
        quotes = (
            df[df["theme"] == row.theme].sort_values("severity", ascending=False)["text"].head(6).tolist()
        )
        if mock:
            body = (
                f"# PRD (MOCK DRAFT): {row.theme}\n\n## Problem Statement\n{row.description}\n\n## Evidence\n"
                f"- {row.reviews} reviews, avg rating {row.avg_rating}, RICE {row.rice_score}\n"
                + "".join(f"- \"{q}\"\n" for q in quotes)
                + "\n_Mock mode: run with an API key for a real draft._\n"
            )
        else:
            user = (
                f"Theme: {row.theme}\nDescription: {row.description}\nReviews: {row.reviews}\n"
                f"Avg rating: {row.avg_rating}\nRICE score: {row.rice_score}\nTop review quotes:\n"
                + "\n".join(f"- {q}" for q in quotes)
            )
            body = call_llm(SYSTEM, user, max_tokens=1500)
        path = out_dir / f"{row.rank:02d}-{slug(row.theme)}.md"
        path.write_text(body, encoding="utf-8")
        prds[row.theme] = {"path": str(path), "text": body, "rice": row.rice_score}
    return prds
