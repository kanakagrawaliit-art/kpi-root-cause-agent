from functools import lru_cache
import pandas as pd
from kpi_rca.config import settings


@lru_cache(maxsize=1)  # load once, then reuse the same DataFrame on later calls
def load_kpi_df() -> pd.DataFrame:
    # If DATABASE_URL is configured, read from the SQL warehouse via SQLAlchemy
    if settings.database_url:
        from sqlalchemy import create_engine
        engine = create_engine(settings.database_url)
        return pd.read_sql("SELECT * FROM kpi_daily", engine, parse_dates=["date"])
    # Otherwise read the local CSV, converting the "date" column to real dates
    return pd.read_csv(settings.kpi_data_path, parse_dates=["date"])


@lru_cache(maxsize=1)
def load_events_df() -> pd.DataFrame:
    # Events (releases, campaigns) are small, so CSV is enough
    return pd.read_csv(settings.events_data_path, parse_dates=["date"])


def parse_period(period: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """'2024-05-01 to 2024-05-07' -> (Timestamp, Timestamp)"""
    try:
        # Split on " to " and convert both halves to timestamps
        start, end = [p.strip() for p in period.split(" to ")]
        return pd.Timestamp(start), pd.Timestamp(end)
    except Exception:
        # Clear error message so the LLM can correct its own tool call
        raise ValueError(f"Period must look like 'YYYY-MM-DD to YYYY-MM-DD', got '{period}'")


def get_slice(period: str, filters: dict | None = None) -> pd.DataFrame:
    """Return only the rows inside a period that also match the filters."""
    df = load_kpi_df()
    start, end = parse_period(period)
    # Keep rows whose date falls inside [start, end]
    df = df[(df["date"] >= start) & (df["date"] <= end)]
    for col, val in (filters or {}).items():
        if str(val).lower() == "all":       # "all" means no filtering on this column
            continue
        if col not in df.columns:
            raise ValueError(f"Unknown filter column '{col}'")
        # Case-insensitive match, e.g. {"device": "android"}
        df = df[df[col].astype(str).str.lower() == str(val).lower()]
    if df.empty:
        raise ValueError(f"No data for period={period}, filters={filters}")
    return df


def default_periods() -> tuple[str, str]:
    """Last 7 days in the data vs the 7 days before (used when user gives none)."""
    last = load_kpi_df()["date"].max()
    cur = f"{(last - pd.Timedelta(days=6)).date()} to {last.date()}"
    base = f"{(last - pd.Timedelta(days=13)).date()} to {(last - pd.Timedelta(days=7)).date()}"
    return cur, base