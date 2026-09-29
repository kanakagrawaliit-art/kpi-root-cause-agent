from kpi_rca.tools.kpi_tools import (get_kpi_value, compare_periods,
                                     breakdown_by_dimension, rank_contributors, query_data)
from kpi_rca.tools.event_tools import get_event_context

# The complete tool list the LLM can choose from (matches the 6 tools in the diagram)
ALL_TOOLS = [get_kpi_value, compare_periods, breakdown_by_dimension,
             rank_contributors, query_data, get_event_context]