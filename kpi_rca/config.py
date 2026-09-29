import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Read .env and put its values into environment variables.
# langchain-openai automatically picks up OPENAI_API_KEY from there.
load_dotenv()

# Project root = two folders above this file (kpi_rca/config.py -> repo root)
ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)  # frozen = settings can't be changed accidentally at runtime
class Settings:
    # Which OpenAI chat model the agent uses (falls back to gpt-4o-mini)
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Where the CSV data files live
    kpi_data_path: Path = ROOT / "data" / "raw" / "kpi_daily.csv"
    events_data_path: Path = ROOT / "data" / "raw" / "events.csv"

    # If set, the loader reads from a SQL database instead of CSV
    database_url: str | None = os.getenv("DATABASE_URL")

    max_reasoning_steps: int = 6   # soft cap: written into the prompt for the LLM
    recursion_limit: int = 40      # hard cap: LangGraph stops the loop at this many steps


# One shared instance imported everywhere as: from kpi_rca.config import settings
settings = Settings()