from langchain.tools import tool, ToolRuntime
from langgraph.types import Command

from kpi_rca.data.loader import load_events_df, parse_period
from kpi_rca.tools._helpers import run_tool


@tool
def get_event_context(period: str, runtime: ToolRuntime) -> Command:
    """List releases, campaigns and other events that happened during a period ('YYYY-MM-DD to YYYY-MM-DD')."""
    def work():
        start, end = parse_period(period)
        ev = load_events_df()
        # Keep only events that fall inside the requested period
        ev = ev[(ev["date"] >= start) & (ev["date"] <= end)]
        rows = [{"date": str(r.date.date()), "type": r.event_type, "description": r.description}
                for r in ev.itertuples()]
        # Every event found is also saved as evidence in state
        findings = [f"Event on {r['date']}: {r['description']}" for r in rows]
        return {"period": period, "events": rows}, findings, []
    return run_tool(runtime, "get_event_context", {"period": period}, work)