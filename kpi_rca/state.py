import operator
from typing import Annotated
from langchain.agents import AgentState   # already includes the `messages` field


class RCAState(AgentState):
    parsed_request: dict                                   # the AnalysisRequest as a dict
    # operator.add is the "reducer": new values are appended (lists) or summed (int)
    tool_results: Annotated[list[dict], operator.add]      # past tool outputs
    current_hypotheses: Annotated[list[str], operator.add] # working hypotheses
    evidence: Annotated[list[str], operator.add]           # key findings
    iteration_count: Annotated[int, operator.add]          # +1 per tool call