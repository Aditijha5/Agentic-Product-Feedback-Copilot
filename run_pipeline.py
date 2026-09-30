"""Run the full pipeline: classify -> themes -> RICE -> PRDs -> (optional) Jira."""
import argparse
import json

from .classify import classify_reviews
from .config import OUT, have_api_key
from .ingest import load_reviews
from .jira_push import build_tickets, push_tickets
from .prd import draft_prds
from .prioritize import rice_table
from .themes import assign_themes


def main():
    p = argparse.ArgumentParser(description="Agentic Product Feedback Copilot")
    p.add_argument("--input", default="data/reviews.csv")
    p.add_argument("--prompt-version", default="v2")
    p.add_argument("--top-n", type=int, default=3)
    p.add_argument("--max-themes", type=int, default=6)
    p.add_argument("--mock", action="store_true", help="No API calls; keyword rules. For testing only.")
    p.add_argument("--push-jira", action="store_true", help="Actually create Jira tickets (asks per ticket).")
    a = p.parse_args()

    mock = a.mock or not have_api_key()
    if mock:
        print("** MOCK MODE: no LLM calls. Outputs are for testing only. **")
    OUT.mkdir(exist_ok=True)

    df = load_reviews(a.input)
    print(f"[1/5] Classifying {len(df)} reviews (prompt {a.prompt_version})")
    df = classify_reviews(df, version=a.prompt_version, mock=mock)

    print("[2/5] Grouping into themes")
    df, meta = assign_themes(df, mock=mock, max_themes=a.max_themes)

    print("[3/5] RICE prioritization")
    ranked = rice_table(df, meta)

    df.to_csv(OUT / "reviews_classified.csv", index=False)
    ranked.to_csv(OUT / "themes_ranked.csv", index=False)
    (OUT / "themes_meta.json").write_text(json.dumps(meta, indent=2))
    print(ranked[["rank", "theme", "reviews", "reach_pct", "impact", "effort_weeks_assumed", "rice_score"]].to_string(index=False))

    print(f"[4/5] Drafting PRDs for top {a.top_n}")
    prds = draft_prds(df, ranked, top_n=a.top_n, mock=mock)

    print("[5/5] Jira tickets")
    push_tickets(build_tickets(prds), push=a.push_jira)
    print("\nDone. See outputs/ (CSV files are ready for Power BI).")


if __name__ == "__main__":
    main()
