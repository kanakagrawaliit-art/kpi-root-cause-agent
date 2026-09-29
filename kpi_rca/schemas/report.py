from typing import Literal
from pydantic import BaseModel, Field


class RCAReport(BaseModel):
    """Final structured root-cause analysis."""
    # Field descriptions are sent to the LLM, so they act as instructions
    summary: str = Field(description="2-4 sentence plain-English answer to the user's question")
    kpi_change: dict = Field(description="Keys: metric, baseline, current, absolute_change, pct_change")
    top_drivers: list[dict] = Field(description="Ranked drivers. Each: dimension, segment, contribution, share_of_change, note")
    evidence: list[str] = Field(description="Key findings, each traceable to a tool result")
    # Literal restricts the model to exactly one of these three values
    confidence: Literal["High", "Medium", "Low"]
    recommended_next_checks: list[str]