import pandas as pd
from kpi_rca.schemas.report import RCAReport


def to_narrative(r: RCAReport) -> str:
    """Human-readable text: summary, evidence, confidence, next checks."""
    lines = [r.summary, "", "Evidence:"]
    lines += [f"  - {e}" for e in r.evidence]
    lines += ["", f"Confidence: {r.confidence}", "", "Recommended next checks:"]
    lines += [f"  - {c}" for c in r.recommended_next_checks]
    return "\n".join(lines)


def drivers_table(r: RCAReport) -> str:
    """Table-ready top drivers (requires the `tabulate` package)."""
    if not r.top_drivers:
        return "(no drivers identified)"
    return pd.DataFrame(r.top_drivers).to_markdown(index=False)


def to_json(r: RCAReport) -> str:
    """Structured JSON of the full RCAReport."""
    return r.model_dump_json(indent=2)