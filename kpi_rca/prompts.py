from kpi_rca.config import settings

# Static rules: these match the six bullet points in the diagram's System Prompt box
SYSTEM_RULES = f"""You are a KPI root-cause analyst.
Rules:
- Investigate the KPI change. Start by confirming it with compare_periods.
- Quantify drivers with data: use breakdown_by_dimension and rank_contributors across
  dimensions (device, country, channel, product). Drill down with filters when a segment stands out.
- Use the available tools. Every number you report must come from a tool result.
- Never invent data. If evidence is missing, say so and lower your confidence.
- Check get_event_context for releases or campaigns overlapping the change.
- Stop calling tools once the evidence is sufficient, or when iteration_count reaches
  {settings.max_reasoning_steps}. Then produce the final structured report."""


def format_state_context(state: dict) -> str:
    """Turn live state into text the LLM reads before every decision."""
    req = state.get("parsed_request", {})
    hyps = state.get("current_hypotheses", [])
    ev = state.get("evidence", [])
    return (
        "\n\n--- CURRENT STATE ---\n"
        f"parsed_request: {req}\n"
        f"iteration_count: {state.get('iteration_count', 0)}\n"
        # Only the most recent items are shown, to keep the prompt small
        f"current_hypotheses: {hyps[-6:] or 'none yet'}\n"
        f"evidence so far: {ev[-10:] or 'none yet'}\n"
    )