# Architecture and Product Thinking

## Who this is for
A product manager or APM who has to turn a flood of unstructured feedback into a short, defensible list of what to build next.

## Job to be done
"Given thousands of reviews, tell me which few problems matter most, why, and draft the work so I can decide quickly."

## Agent roles
| Agent | Input | Output | Why an LLM |
|---|---|---|---|
| Classifier | Review text, rating | Category, sentiment, severity 1-5, short topic | Understanding free-text language |
| Theme grouper | List of topics with counts | Up to 6 named themes with a one-line description and effort estimate | Semantic grouping of near-duplicate topics |
| PRD writer | Theme stats and top quotes | PRD: problem, evidence, user stories, acceptance criteria, success metrics | Structured drafting from evidence |

Steps with no LLM: ingestion, RICE scoring, evaluation, and Jira calls. These are deterministic so results can be checked.

## Where the human decides
1. **Prompt design and labels:** the PM defines categories and a severity rubric.
2. **Priorities:** RICE ranks, but the PM can override the order.
3. **Ticket creation:** every ticket needs an explicit approval.

## How to know if it works (planned measures)
- Classifier accuracy on a hand-labeled sample, compared across prompt versions.
- Agreement between the ranking and a PM's own manual ranking of the same themes.
- Time to triage a batch manually vs reviewing the agent's draft.
These are the measures the repo is set up to produce; no results are claimed here.

## Failure modes considered
- Misclassification of sarcasm or mixed reviews, mitigated with a "primary complaint" rule and evaluation.
- Over-weighting a vocal minority, mitigated with confidence discounting and the reach limitation noted.
- Invented details in PRDs, mitigated by instructing the writer to use only supplied evidence.

## What I would do next
- Add a time dimension to catch emerging issues (theme volume by week).
- Segment by app version to link complaints to releases.
- Feed approved/rejected decisions back in to tune prioritization.
