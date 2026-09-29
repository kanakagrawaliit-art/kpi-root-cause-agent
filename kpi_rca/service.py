import uuid
from kpi_rca.agent import build_agent
from kpi_rca.config import settings
from kpi_rca.schemas.report import RCAReport
from kpi_rca.schemas.request import AnalysisRequest

_agent = None   # cached so the agent is built only once per process


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def run_analysis(request: AnalysisRequest, thread_id: str | None = None) -> RCAReport:
    result = get_agent().invoke(
        {
            # The user's question becomes the first chat message
            "messages": [{"role": "user", "content": request.question}],
            # Seed the shared state (Box 2 -> Box 3 arrow in the diagram)
            "parsed_request": request.model_dump(),
            "tool_results": [], "current_hypotheses": [], "evidence": [],
            "iteration_count": 0,
        },
        config={
            # thread_id tells InMemorySaver which conversation's state to use
            "configurable": {"thread_id": thread_id or str(uuid.uuid4())},
            # Hard safety cap on total graph steps
            "recursion_limit": settings.recursion_limit,
        },
    )
    # ToolStrategy stores the validated RCAReport object under this key
    return result["structured_response"]