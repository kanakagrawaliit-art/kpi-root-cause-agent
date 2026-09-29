import numpy as np
import pandas as pd

# Metric registry: "ratio" metrics divide two columns; "sum" metrics add one column.
# To support a new KPI, add one line here.
METRICS = {
    "checkout_conversion": {"type": "ratio", "num": "conversions", "den": "sessions"},
    "sessions":    {"type": "sum", "col": "sessions"},
    "conversions": {"type": "sum", "col": "conversions"},
    "revenue":     {"type": "sum", "col": "revenue"},
}
# Columns the agent is allowed to slice by
DIMENSIONS = ["device", "country", "channel", "product"]


def check_metric(metric: str):
    # Raises a helpful error the LLM can read and fix
    if metric not in METRICS:
        raise ValueError(f"Unknown metric '{metric}'. Valid: {list(METRICS)}")


def check_dimension(dim: str):
    if dim not in DIMENSIONS:
        raise ValueError(f"Unknown dimension '{dim}'. Valid: {DIMENSIONS}")


def metric_value(df: pd.DataFrame, metric: str) -> float:
    """Compute one KPI over a DataFrame slice."""
    check_metric(metric)
    spec = METRICS[metric]
    if spec["type"] == "ratio":
        # Ratio of totals (NOT the average of daily ratios), guarded against divide-by-zero
        den = df[spec["den"]].sum()
        return float(df[spec["num"]].sum() / den) if den else 0.0
    return float(df[spec["col"]].sum())


def segment_contributions(cur: pd.DataFrame, base: pd.DataFrame,
                          metric: str, dimension: str) -> pd.DataFrame:
    """Per-segment contribution to the total change of the metric."""
    check_metric(metric); check_dimension(dimension)
    spec = METRICS[metric]

    if spec["type"] == "ratio":
        num, den = spec["num"], spec["den"]
        # Totals of numerator and denominator per segment, for each period
        c = cur.groupby(dimension)[[num, den]].sum()
        b = base.groupby(dimension)[[num, den]].sum()
        # Outer join so segments present in only one period are kept (filled with 0)
        t = c.join(b, how="outer", lsuffix="_c", rsuffix="_b").fillna(0)

        # w = each segment's share of total traffic (the "mix"); r = its conversion rate
        w_c = t[f"{den}_c"] / t[f"{den}_c"].sum()
        w_b = t[f"{den}_b"] / t[f"{den}_b"].sum()
        r_c = (t[f"{num}_c"] / t[f"{den}_c"]).replace([np.inf, -np.inf], 0).fillna(0)
        r_b = (t[f"{num}_b"] / t[f"{den}_b"]).replace([np.inf, -np.inf], 0).fillna(0)

        out = pd.DataFrame({
            "segment": t.index.astype(str),
            "baseline_value": r_b.values,
            "current_value": r_c.values,
            # rate effect: w_c*(r_c-r_b)   +   mix effect: (w_c-w_b)*r_b
            # Summed over all segments this equals total_current - total_baseline exactly.
            "contribution": (w_c * (r_c - r_b) + (w_c - w_b) * r_b).values,
        })
    else:
        # Additive metrics (sessions, revenue): contribution is just the difference
        col = spec["col"]
        c = cur.groupby(dimension)[col].sum()
        b = base.groupby(dimension)[col].sum()
        t = pd.concat([b.rename("b"), c.rename("c")], axis=1).fillna(0)
        out = pd.DataFrame({
            "segment": t.index.astype(str),
            "baseline_value": t["b"].values,
            "current_value": t["c"].values,
            "contribution": (t["c"] - t["b"]).values,
        })

    # Extra readable columns the LLM can quote
    out["change"] = out["current_value"] - out["baseline_value"]
    out["change_pct"] = np.where(out["baseline_value"] != 0,
                                 out["change"] / out["baseline_value"] * 100, np.nan)
    # Share of the overall change explained by this segment (e.g. 0.68 = 68%)
    total = out["contribution"].sum()
    out["share_of_total_change"] = out["contribution"] / total if total else 0.0
    return out.round(4)