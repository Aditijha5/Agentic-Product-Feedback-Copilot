# Agentic Product Feedback Copilot

**By [Aditi Jha](https://github.com/Aditijha5)**

A product-thinking prototype: an AI agent pipeline that turns raw app-store reviews into a prioritized product backlog. It classifies reviews, groups them into themes, ranks the themes with RICE, drafts PRDs for the top ones, and creates Jira tickets only after a human approves each one.

> **Status:** working prototype. The full pipeline runs end to end in a keyword-based mock mode (covered by smoke tests). The LLM-backed steps are implemented but have not been benchmarked on a large real dataset, so this repo makes no accuracy or time-saving claims. The evaluation script is included so anyone can measure it.

## The problem
Product teams receive thousands of reviews and support messages. Triage is slow and subjective, and priorities often follow whoever is loudest. The question behind this project: how much of the first-pass work (labeling, clustering, drafting) can agents do, while the PM keeps control of prioritization and approval?

## The idea in one picture
```
reviews -> Classifier agent -> Theme agent -> RICE scoring -> PRD agent -> Human approval -> Jira
           (what kind of      (which problems  (plain Python,  (what to     (PM says yes/no
            feedback is it?)   repeat?)         no LLM math)    build, why)  per ticket)
```

## Design decisions (the product thinking)
- **Agents do language work, code does math.** RICE is computed deterministically so rankings are reproducible and auditable.
- **Human in the loop.** Nothing reaches Jira without an explicit yes per ticket; the PM owns the decision.
- **Confidence-weighted ranking.** Themes with few reviews are discounted (`min(1, reviews / 20)`), so a small loud group can't outrank a well-supported problem.
- **Prompts are versioned and testable.** `classifier_v1` (basic) vs `classifier_v2` (definitions, severity rubric, examples) can be compared on a hand-labeled set with `src/evaluate.py`.
- **Honest about assumptions.** Effort in RICE is an estimate, not something reviews can reveal.

More detail: [docs/architecture.md](docs/architecture.md). Example of the PRD the pipeline produces: [docs/sample_prd.md](docs/sample_prd.md).

## Run it
```bash
pip install -r requirements.txt
cp env.example .env                 # add ANTHROPIC_API_KEY (optional; without it, mock mode runs)
python -m src.run_pipeline --input data/sample_reviews.csv
```
Outputs go to `outputs/`: classified reviews, ranked themes, and PRD drafts (CSVs are Power BI ready). Use `--push-jira` with Jira credentials in `.env` to create tickets after per-ticket approval. To measure the classifier on your own labeled reviews: `python -m src.evaluate`.

`data/sample_reviews.csv` is synthetic test data, not real user feedback.

## Limitations
- Review volume is a proxy for reach, and reviewers are not representative of all users.
- Effort estimates are assumptions.
- LLM labels can be inconsistent, which is why the evaluation step exists.
- Scraping the Play Store may conflict with its terms; a public dataset is safer.

## Tech stack
Python, pandas, Claude API (Anthropic SDK), Jira REST API, Power BI, pytest.
