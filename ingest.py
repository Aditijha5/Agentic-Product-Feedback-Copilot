"""Load reviews from CSV, or scrape them from the Play Store."""
import argparse

import pandas as pd

REQUIRED = {"review_id", "text", "rating"}


def load_reviews(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"review_id": str})
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")
    df = df.dropna(subset=["text", "rating"]).copy()
    df["rating"] = df["rating"].astype(int)
    df["text"] = df["text"].astype(str).str.strip()
    return df[df["text"].str.len() > 3].reset_index(drop=True)


def scrape_play_store(app_id: str, n: int = 600, lang: str = "en", country: str = "in") -> pd.DataFrame:
    """Check the Play Store terms before scraping; a Kaggle review dataset is the safer alternative."""
    from google_play_scraper import Sort, reviews

    result, _ = reviews(app_id, lang=lang, country=country, sort=Sort.NEWEST, count=n)
    df = pd.DataFrame(result)
    return pd.DataFrame(
        {
            "review_id": df["reviewId"].astype(str),
            "text": df["content"],
            "rating": df["score"],
            "date": df["at"],
        }
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Scrape Play Store reviews to CSV")
    p.add_argument("app_id", help="e.g. com.example.app")
    p.add_argument("--n", type=int, default=600)
    p.add_argument("--out", default="data/reviews.csv")
    a = p.parse_args()
    scrape_play_store(a.app_id, a.n).to_csv(a.out, index=False)
    print(f"Saved reviews to {a.out}")
