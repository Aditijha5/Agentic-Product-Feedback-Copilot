"""Evaluate classifier prompt versions against a hand-labeled set.

Usage: python -m src.evaluate --reviews data/reviews.csv --labels data/labeled_reviews.csv --versions v1 v2
labels CSV columns: review_id, true_category (one of bug, performance, ux, feature_request, pricing, praise, other)
"""
import argparse
import json

import pandas as pd

from .classify import classify_reviews
from .config import CATEGORIES, OUT, have_api_key
from .ingest import load_reviews


def evaluate(reviews_path: str, labels_path: str, version: str, mock: bool) -> dict:
    reviews = load_reviews(reviews_path)
    labels = pd.read_csv(labels_path, dtype={"review_id": str})
    sample = reviews.merge(labels[["review_id", "true_category"]], on="review_id")
    pred = classify_reviews(sample, version=version, mock=mock)
    ok = pred["category"] == pred["true_category"]
    per_class = {}
    for c in CATEGORIES:
        tp = int(((pred["category"] == c) & (pred["true_category"] == c)).sum())
        fp = int(((pred["category"] == c) & (pred["true_category"] != c)).sum())
        fn = int(((pred["category"] != c) & (pred["true_category"] == c)).sum())
        if tp + fp + fn:
            per_class[c] = {
                "precision": round(tp / (tp + fp), 2) if tp + fp else None,
                "recall": round(tp / (tp + fn), 2) if tp + fn else None,
                "support": int((pred["true_category"] == c).sum()),
            }
    OUT.mkdir(exist_ok=True)
    pred.loc[~ok, ["review_id", "text", "true_category", "category"]].to_csv(OUT / f"misclassified_{version}.csv", index=False)
    result = {"version": version, "n": len(pred), "accuracy": round(float(ok.mean()), 3), "per_class": per_class, "mock": mock}
    (OUT / f"eval_{version}.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--reviews", default="data/reviews.csv")
    p.add_argument("--labels", default="data/labeled_reviews.csv")
    p.add_argument("--versions", nargs="+", default=["v1", "v2"])
    p.add_argument("--mock", action="store_true")
    a = p.parse_args()
    mock = a.mock or not have_api_key()
    for v in a.versions:
        r = evaluate(a.reviews, a.labels, v, mock)
        print(f"{v}: accuracy {r['accuracy']:.1%} on {r['n']} reviews" + ("  [MOCK, not a real result]" if mock else ""))
