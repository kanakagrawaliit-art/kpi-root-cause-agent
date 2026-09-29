import pytest
from kpi_rca.data.loader import get_slice
from kpi_rca.data.metrics import metric_value, segment_contributions

# The two periods from your diagram's example
CUR, BASE = "2024-05-01 to 2024-05-07", "2024-04-24 to 2024-04-30"


# Runs 3 metrics x 4 dimensions = 12 test cases automatically
@pytest.mark.parametrize("metric", ["checkout_conversion", "sessions", "revenue"])
@pytest.mark.parametrize("dim", ["device", "country", "channel", "product"])
def test_contributions_sum_to_total_change(metric, dim):
    cur, base = get_slice(CUR), get_slice(BASE)
    table = segment_contributions(cur, base, metric, dim)
    # The true overall change, computed directly (no segments)
    total = metric_value(cur, metric) - metric_value(base, metric)
    # Segment contributions must add up to it (small tolerance for rounding)
    assert abs(table["contribution"].sum() - total) < 1e-3 * max(1, abs(total)) + 1e-6