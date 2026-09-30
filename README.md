# Agentic Product Feedback Copilot

**Built by [Aditi Jha](https://github.com/Aditijha5)**

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
pip install -r requirements.txt
cp .env.example .env        # then add your ANTHROPIC_API_KEY

# 1. Get reviews (CSV columns: review_id, text, rating)
python -m src.ingest com.example.app --n 600     # or use your own CSV

# 2. Run the pipeline
python -m src.run_pipeline --input data/reviews.csv --prompt-version v2

# 3. Optional: create Jira tickets (asks before each one)
python -m src.run_pipeline --input data/reviews.csv --push-jira
```

Jira is optional; set `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY` in `.env` to use `--push-jira`.

Without an API key the pipeline falls back to a keyword-based mock mode so you can test the plumbing. Mock output is for testing only and should not be treated as a result.

## Outputs
Everything is written to `outputs/`:
- `reviews_classified.csv`: every review with its category, severity, topic, and theme
- `themes_ranked.csv`: themes with reach, impact, confidence, effort, and RICE score
- `prds/`: one Markdown PRD per top theme

The two CSVs load directly into Power BI for a theme-ranking and category-mix dashboard.

## Evaluating the classifier
1. Hand-label a sample of reviews in `data/labeled_reviews.csv` with columns `review_id,true_category` before looking at model output.
2. Run:
```bash
   python -m src.evaluate --reviews data/reviews.csv --labels data/labeled_reviews.csv --versions v1 v2
```
3. Read `outputs/eval_*.json` for accuracy and per-category precision and recall, and `outputs/misclassified_*.csv` to see where the model disagrees with you. Use those patterns to improve the prompt.

## Project structure
```
src/        pipeline code (ingest, classify, themes, prioritize, prd, jira_push, evaluate, run_pipeline)
prompts/    classifier prompt versions v1 and v2
data/       input reviews and labeled evaluation set
tests/      smoke tests that run the pipeline in mock mode
outputs/    generated results (git-ignored)
```

## Limitations
- Review volume is only a proxy for reach, and people who write reviews are not representative of all users.
- Effort in RICE is an assumption supplied by the theme agent or defaults in `src/config.py`; reviews can't reveal engineering cost.
- LLM labels can be inconsistent, which is why the evaluation step exists.
- Scraping the Play Store may conflict with its terms of service; a public review dataset is a safer source.
- Jira tickets are created on a demo board, not inside a real team workflow.

## Tech stack
Python, pandas, Claude API (Anthropic SDK), Jira REST API, Power BI, pytest.

## Author
**Aditi Jha**

## Author
**Aditi Jha**, B.Tech Mechanical Engineering, IIITDM Jabalpur. Interested in product management, user research, and AI-driven product workflows.
GitHub: [Aditijha5](https://github.com/Aditijha5)
