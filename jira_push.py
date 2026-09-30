"""Step 5: human-in-the-loop Jira ticket creation. Dry-run unless --push-jira is passed."""
import os

import requests


def _adf(text: str) -> dict:
    lines = [ln for ln in text.split("\n") if ln.strip()][:60]
    return {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": ln[:900]}]} for ln in lines],
    }


def build_tickets(prds: dict) -> list:
    return [
        {
            "summary": f"[Feedback Copilot] {theme}",
            "description": f"RICE score: {info['rice']}\n\n{info['text']}",
        }
        for theme, info in prds.items()
    ]


def push_tickets(tickets: list, push: bool = False, ask: bool = True) -> list:
    created = []
    for t in tickets:
        print(f"\n--- Proposed ticket: {t['summary']}")
        print(t["description"][:400], "...")
        if not push:
            print("(dry run: not sent to Jira)")
            continue
        if ask and input("Create this ticket? [y/N] ").strip().lower() != "y":
            print("Skipped.")
            continue
        base = os.environ["JIRA_BASE_URL"].rstrip("/")
        resp = requests.post(
            f"{base}/rest/api/3/issue",
            auth=(os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"]),
            json={
                "fields": {
                    "project": {"key": os.environ["JIRA_PROJECT_KEY"]},
                    "summary": t["summary"],
                    "description": _adf(t["description"]),
                    "issuetype": {"name": "Task"},
                    "labels": ["feedback-copilot"],
                }
            },
            timeout=30,
        )
        resp.raise_for_status()
        key = resp.json()["key"]
        created.append(key)
        print(f"Created {key}")
    return created
