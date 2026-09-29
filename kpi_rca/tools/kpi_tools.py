from langchain.tools import tool, ToolRuntime
from langgraph.types import Command

from kpi_rca.data.loader import get_slice
from kpi_rca.data.metrics import (check_dimension, check_metric,
                                  metric_value, segment_contributions)
from kpi_rca.tools._helpers import run_tool


# ---- Tool 1: single KPI value ------------------------------------------------
@tool  # turns the function into a LangChain tool; the docstring is the description
def get_kpi_value(metric: str, period: str, runtime: ToolRuntime,
                  filters: dict | None = None) -> Command:
    """Get the value of one KPI for one period ('YYYY-MM-DD to YYYY-MM-DD'), optionally filtered."""
    # `runtime` is injected by LangChain and hidden from the LLM's tool schema
    args = {"metric": metric, "period": period, "filters": filters}

    def work():
        check_metric(metric)
        val = metric_value(get_slice(period, filters), metric)
        # Return (payload, evidence, hypotheses); this tool adds no evidence itself
        return {"metric": metric, "period": period, "filters": filters, "value": round(val, 6)}, [], []
    return run_tool(runtime, "get_kpi_value", args, work)


# ---- Tool 2: compare two periods --------------------------------------------
@tool
def compare_periods(metric: str, current_period: str, baseline_period: str,
                    runtime: ToolRuntime, filters: dict | None = None) -> Command:
    """Compare a KPI between the current and baseline period. Returns baseline, current, absolute and % change."""
    args = {"metric": metric, "current_period": current_period,
            "baseline_period": baseline_period, "filters": filters}

    def work():
        check_metric(metric)
        cur = metric_value(get_slice(current_period, filters), metric)
        base = metric_value(get_slice(baseline_period, filters), metric)
        pct = (cur - base) / base * 100 if base else None   # avoid divide-by-zero
        payload = {"metric": metric, "baseline": round(base, 6), "current": round(cur, 6),
                   "absolute_change": round(cur - base, 6),
                   "pct_change": round(pct, 2) if pct is not None else None}
        # Automatically log a human-readable finding into state.evidence
        ev = [f"{metric} moved {pct:+.1f}% ({base:.4f} -> {cur:.4f}) vs baseline"] if pct is not None else []
        return payload, ev, []
    return run_tool(runtime, "compare_periods", args, work)


# ---- Tool 3: split a KPI by one dimension -----------------------------------
@tool
def breakdown_by_dimension(metric: str, dimension: str, period: str,
                           runtime: ToolRuntime, filters: dict | None = None) -> Command:
    """Show a KPI split by one dimension (device, country, channel, product) for a single period."""
    args = {"metric": metric, "dimension": dimension, "period": period, "filters": filters}

    def work():
        check_metric(metric); check_dimension(dimension)
        df = get_slice(period, filters)
        # One row per segment value, e.g. device=iOS / Android / Web
        rows = [{"segment": str(seg), "value": round(metric_value(g, metric), 6), "rows": len(g)}
                for seg, g in df.groupby(dimension)]
        return {"metric": metric, "dimension": dimension, "period": period, "segments": rows}, [], []
    return run_tool(runtime, "breakdown_by_dimension", args, work)


# ---- Tool 4: rank segments by contribution to the change --------------------
@tool
def rank_contributors(metric: str, dimension: str, current_period: str,
                      baseline_period: str, runtime: ToolRuntime,
                      filters: dict | None = None, top_n: int = 5) -> Command:
    """Rank the segments of a dimension by how much each contributed to the KPI change (current vs baseline)."""
    args = {"metric": metric, "dimension": dimension, "current_period": current_period,
            "baseline_period": baseline_period, "filters": filters, "top_n": top_n}

    def work():
        cur = get_slice(current_period, filters)
        base = get_slice(baseline_period, filters)
        table = segment_contributions(cur, base, metric, dimension)  # math from metrics.py
        total = table["contribution"].sum()

        # If the KPI fell, "biggest contributor" means most negative, so flip the sign
        # before sorting so the main driver is always first.
        sign = 1 if total >= 0 else -1
        table = table.assign(_k=table["contribution"] * sign).sort_values("_k", ascending=False).drop(columns="_k")
        top = table.head(top_n)
        payload = {"metric": metric, "dimension": dimension,
                   "total_change": round(float(total), 6),
                   "ranked": top.to_dict(orient="records")}

        ev, hyp = [], []
        if len(top):
            t = top.iloc[0]   # the #1 driver
            ev.append(f"{dimension}={t['segment']} explains {t['share_of_total_change']:.0%} of the "
                      f"{metric} change ({t['baseline_value']:.4f} -> {t['current_value']:.4f})")
            # Auto-create a hypothesis only if the driver is big (over 20% of the change)
            if t["share_of_total_change"] > 0.2:
                hyp.append(f"{dimension}={t['segment']} is a major driver "
                           f"({t['share_of_total_change']:.0%} of change)")
        return payload, ev, hyp
    return run_tool(runtime, "rank_contributors", args, work)


# ---- Tool 5: flexible aggregated query --------------------------------------
@tool
def query_data(group_by: list[str], metrics: list[str], period: str,
               runtime: ToolRuntime, filters: dict | None = None, limit: int = 20) -> Command:
    """Flexible aggregated query: compute one or more KPIs grouped by one or more dimensions for one period. Max 50 rows."""
    args = {"group_by": group_by, "metrics": metrics, "period": period,
            "filters": filters, "limit": limit}

    def work():
        if not group_by:
            raise ValueError("group_by needs at least one dimension")
        for d in group_by: check_dimension(d)   # validate every dimension
        for m in metrics: check_metric(m)       # validate every metric
        df = get_slice(period, filters)
        rows = []
        for keys, g in df.groupby(group_by):
            # groupby returns a tuple for multiple keys, a scalar for one key
            keys = keys if isinstance(keys, tuple) else (keys,)
            row = dict(zip(group_by, map(str, keys)))
            row.update({m: round(metric_value(g, m), 6) for m in metrics})
            rows.append(row)
        # Cap output size so a huge table can't flood the LLM's context
        return {"rows": rows[:min(limit, 50)], "total_rows": len(rows)}, [], []
    return run_tool(runtime, "query_data", args, work)