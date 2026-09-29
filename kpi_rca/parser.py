from kpi_rca.data.loader import default_periods
from kpi_rca.data.metrics import METRICS
from kpi_rca.schemas.request import AnalysisRequest


def infer_metric(question: str) -> str:
    q = question.lower().replace("_", " ")
    for m in METRICS:
        if m.replace("_", " ") in q:
            return m
    raise ValueError(f"Could not infer a KPI from the question. Pass --metric. Valid: {list(METRICS)}")


def parse_request(question: str, metric: str | None = None,
                  current_period: str | None = None,
                  baseline_period: str | None = None,
                  filters: dict | None = None) -> AnalysisRequest:
    cur_default, base_default = default_periods()
    return AnalysisRequest(
        question=question,
        metric=metric or infer_metric(question),
        current_period=current_period or cur_default,
        baseline_period=baseline_period or base_default,
        filters=filters or {},
    )