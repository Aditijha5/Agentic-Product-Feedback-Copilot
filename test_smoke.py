"""Smoke tests: run the whole pipeline in mock mode (no API key, no network)."""
from src.classify import classify_reviews
from src.ingest import load_reviews
from src.prioritize import rice_table
from src.themes import assign_themes


def test_pipeline_runs_in_mock_mode():
    df = load_reviews("data/sample_reviews.csv")
    df = classify_reviews(df, mock=True)
    assert df["category"].notna().all()
    df, meta = assign_themes(df, mock=True)
    ranked = rice_table(df, meta)
    assert len(ranked) >= 3
    assert ranked["rice_score"].is_monotonic_decreasing
    assert (ranked["reach_pct"] <= 100).all()


def test_rice_discounts_small_samples():
    df = load_reviews("data/sample_reviews.csv")
    df = classify_reviews(df, mock=True)
    df, meta = assign_themes(df, mock=True)
    ranked = rice_table(df, meta)
    assert (ranked["confidence"] <= 1).all()
