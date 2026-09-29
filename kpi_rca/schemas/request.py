import re
from pydantic import BaseModel, Field, field_validator
from kpi_rca.data.metrics import METRICS

# Enforces the "YYYY-MM-DD to YYYY-MM-DD" format
PERIOD_RE = re.compile(r"^\d{4}-\d{2}-\d{2} to \d{4}-\d{2}-\d{2}$")


class AnalysisRequest(BaseModel):
    # The 5 fields shown in Box 2 of your diagram
    question: str
    metric: str
    current_period: str
    baseline_period: str
    filters: dict = Field(default_factory=dict)   # default {} like the diagram

    @field_validator("metric")
    @classmethod
    def _metric(cls, v):
        # Reject KPIs we have no math for
        if v not in METRICS:
            raise ValueError(f"metric must be one of {list(METRICS)}")
        return v

    @field_validator("current_period", "baseline_period")
    @classmethod
    def _period(cls, v):
        # Reject badly formatted periods before they reach any tool
        if not PERIOD_RE.match(v):
            raise ValueError("period must be 'YYYY-MM-DD to YYYY-MM-DD'")
        return v