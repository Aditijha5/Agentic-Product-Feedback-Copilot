"""Step 3: RICE prioritization.

Reach       = share of actionable reviews in the theme (%), a proxy for affected users
Impact      = mean severity (1-5) rescaled to 0.25-3
Confidence  = min(1, n_reviews / 20), so small samples are discounted
Effort      = person-weeks, an ASSUMPTION supplied by the theme agent / defaults (not derivable from reviews)
RICE        = Reach * Impact * Confidence / Effort
"""
import pandas as pd

from .themes import PRAISE, UNSORTED


def rice_table(df: pd.DataFrame, meta: dict) -> pd.DataFrame:
    act = df[~df["theme"].isin([PRAISE, UNSORTED])]
    total = max(len(act), 1)
    rows = []
    for theme, g in act.groupby("theme"):
        n = len(g)
        reach = 100 * n / total
        impact = max(0.25, round(g["severity"].mean() / 5 * 3, 2))
        confidence = min(1.0, n / 20)
        effort = meta.get(theme, {}).get("effort_weeks", 4)
        rows.append(
            {
                "theme": theme,
                "description": meta.get(theme, {}).get("description", ""),
                "reviews": n,
                "avg_rating": round(g["rating"].mean(), 2),
                "reach_pct": round(reach, 1),
                "impact": impact,
                "confidence": round(confidence, 2),
                "effort_weeks_assumed": effort,
                "rice_score": round(reach * impact * confidence / effort, 2),
            }
        )
    out = pd.DataFrame(rows).sort_values("rice_score", ascending=False).reset_index(drop=True)
    out.insert(0, "rank", out.index + 1)
    return out
