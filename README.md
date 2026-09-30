# Agentic Product Feedback Copilot


An AI agent pipeline that turns raw app-store reviews into a prioritized product backlog. It classifies reviews, groups them into themes, ranks themes with RICE, drafts PRDs for the top ones, and creates Jira tickets only after a human approves each one.

## The problem
Product teams get thousands of reviews and support messages. Triage is slow, subjective, and often decided by whoever shouted loudest. This project explores how far LLM agents can take the first pass (labeling, clustering, drafting) while the PM keeps control of prioritization and approval.

## How it works

```
reviews.csv -> Classifier agent -> Theme agent -> RICE scoring -> PRD agent -> Human approval -> Jira
               (category,          (groups topics  (plain Python,   (top N       (y/N per ticket)
                severity, topic)    into <= 6       no LLM math)     themes)
                                    themes)
                                                        |
                                                        +-> CSV exports -> Power BI dashboard (under progress)
```

| Step | What it does | Where |
|---|---|---|
| Ingest | Loads a CSV of reviews or scrapes the Play Store | `src/ingest.py` |
| Classify | LLM labels each review: category, sentiment, severity (1-5), topic | `src/classify.py`, `prompts/` |
| Themes | LLM groups fine-grained topics into at most 6 actionable themes | `src/themes.py` |
| Prioritize | RICE score per theme, calculated in code | `src/prioritize.py` |
| PRDs | Drafts a PRD with user stories, acceptance criteria, and metrics for the top themes | `src/prd.py` |
| Jira | Shows each proposed ticket and creates it only on your approval | `src/jira_push.py` |
| Evaluate | Compares classifier prompt versions against hand-labeled reviews | `src/evaluate.py` |

## Design decisions
- **The LLM does language work, code does math.** RICE scores are computed deterministically, so rankings are reproducible and auditable.
- **Human in the loop.** Nothing reaches Jira without an explicit `y` per ticket.
- **Prompt versions are first-class.** `prompts/classifier_v1.txt` is a basic prompt; `classifier_v2.txt` adds category definitions, a severity rubric, and examples. The evaluation script compares them on the same labeled set.
- **Low-sample themes are discounted.** Confidence is `min(1, reviews / 20)`, so a theme with few reviews can't outrank a well-supported one.

## RICE as implemented
| Factor | Definition |
|---|---|
| Reach | Share of actionable reviews that fall in the theme (%) |
| Impact | Mean severity (1-5) rescaled to 0.25-3 |
| Confidence | `min(1, reviews / 20)` |
| Effort | Estimated person-weeks (an assumption, see Limitations) |

`RICE = Reach x Impact x Confidence / Effort`

## Quickstart

```bash
pip install -r
