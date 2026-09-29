from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from kpi_rca.config import settings
from kpi_rca.prompts import SYSTEM_RULES, format_state_context
from kpi_rca.schemas.report import RCAReport
from kpi_rca.state import RCAState
from kpi_rca.tools import ALL_TOOLS


@dynamic_prompt   # middleware: runs before EVERY LLM call in the loop
def rca_prompt(request: ModelRequest) -> str:
    """System prompt + live state = the 'Read state' arrow in the diagram."""
    return SYSTEM_RULES + format_state_context(request.state)


def build_agent():
    # Box 5: the Chat LLM. temperature=0 keeps analysis consistent between runs.
    llm = ChatOpenAI(model=settings.openai_model, temperature=0)
    return create_agent(
        model=llm,                              # Box 5: reasons and picks actions
        tools=ALL_TOOLS,                        # Boxes 7-8: tool schemas + executor
        middleware=[rca_prompt],                # Box 4: prompt + current state
        state_schema=RCAState,                  # Box 3: custom state fields
        response_format=ToolStrategy(RCAReport),# Box 10: final structured output
        checkpointer=InMemorySaver(),           # in-memory thread state, no long-term memory
    )