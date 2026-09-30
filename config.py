import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
PROMPTS = ROOT / "prompts"
MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5-5")

CATEGORIES = ["bug", "performance", "ux", "feature_request", "pricing", "praise", "other"]

# Effort (person-weeks) is an ASSUMPTION used for RICE, not something reviews can tell us.
DEFAULT_EFFORT_WEEKS = {
    "bug": 3, "performance": 5, "pricing": 2,
    "feature_request": 6, "ux": 4, "other": 3,
}


def have_api_key() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))
