"""
Synthesizer Node — Final Response Generation

Collects all agent outputs and generates a unified, coherent response.
This is always the last node before END in the LangGraph pipeline.
"""
from datetime import datetime, timezone
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.agent.state import GraphState
from app.services.agent.llm import get_llm
import logging

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are the Response Synthesizer for an ecommerce customer support AI platform.

You have received outputs from one or more specialized agents that handled different
aspects of the customer's query. Your job is to combine their outputs into a single,
unified, professional response.

Rules:
- Combine all agent outputs smoothly — avoid repetition.
- Do NOT add information that wasn't in the agent outputs.
- Keep the tone warm, professional, and helpful.
- If escalation happened, mention the ticket number prominently.
- Use clear formatting (bullet points if listing multiple things).
- Be concise — do not repeat the customer's question back to them.
- Maximum response length: ~300 words.
"""


def synthesizer_node(state: GraphState) -> GraphState:
    """
    Generates the final response by synthesising all agent outputs.
    Populates: state["final_response"], state["timeline"]
    """
    agent_outputs = state.get("agent_outputs", {})
    messages = state.get("messages", [])
    timeline = state.get("timeline", [])

    if not agent_outputs:
        state["final_response"] = (
            "I'm sorry, I wasn't able to fully process your request. "
            "Please try again or contact our support team directly."
        )
        return state

    # Build agent output summary for the LLM
    output_sections: list[str] = []
    for agent_name, output in agent_outputs.items():
        label = agent_name.replace("_", " ").title()
        output_sections.append(f"[{label} Output]\n{output}")

    combined_outputs = "\n\n".join(output_sections)

    # Get original user message for context
    user_text = ""
    if messages:
        user_text = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

    llm = get_llm()

    try:
        prompt = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Customer's original question:\n{user_text}\n\n"
                    f"Agent outputs to synthesise:\n{combined_outputs}"
                )
            ),
        ]

        response = llm.invoke(prompt)
        final_response = response.content.strip()

        timeline.append({
            "step": "Response synthesised",
            "agent": "synthesizer",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": f"Combined outputs from: {list(agent_outputs.keys())}",
        })

    except Exception as e:
        logger.error(f"[synthesizer] Error: {e}")
        # Fallback: concatenate raw outputs
        final_response = "\n\n".join(agent_outputs.values())
        timeline.append({
            "step": "Synthesizer fallback (LLM error)",
            "agent": "synthesizer",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": str(e),
        })

    state["final_response"] = final_response
    state["timeline"] = timeline
    return state
