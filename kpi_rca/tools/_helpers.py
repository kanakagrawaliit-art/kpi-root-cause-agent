import json
from langchain.messages import ToolMessage
from langgraph.types import Command


def run_tool(runtime, tool_name: str, args: dict, work) -> Command:
    """work() -> (payload: dict, evidence: list[str], hypotheses: list[str])"""
    try:
        payload, evidence, hypotheses = work()   # run the tool's actual logic
    except (ValueError, KeyError) as e:
        # Bad metric, bad period, empty data, etc. -> tell the LLM, don't crash
        payload, evidence, hypotheses = {"error": str(e)}, [], []

    update = {
        # 1) The observation the LLM will read next (Box 9 -> Box 5).
        #    tool_call_id links this reply to the LLM's original tool request.
        "messages": [ToolMessage(content=json.dumps(payload, default=str),
                                 tool_call_id=runtime.tool_call_id)],
        # 2) Append the raw result to state memory
        "tool_results": [{"tool": tool_name, "args": args, "result": payload}],
        # 3) Adds 1 to the counter (thanks to operator.add in state.py)
        "iteration_count": 1,
    }
    # Only touch these state fields when the tool produced something
    if evidence:
        update["evidence"] = evidence
    if hypotheses:
        update["current_hypotheses"] = hypotheses
    # Returning Command(update=...) makes LangGraph merge these into state
    return Command(update=update)