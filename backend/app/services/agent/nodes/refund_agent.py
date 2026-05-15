"""
Refund Processing Agent Node

Handles refund eligibility checks and recommendations.
Applies the refund threshold guardrail — amounts above $200 trigger escalation.
"""
from datetime import datetime, timezone
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from app.services.agent.state import GraphState
from app.services.agent.llm import get_llm
from app.services.agent.tools.refunds import check_refund_eligibility, recommend_refund_approval
import logging
import re

logger = logging.getLogger(__name__)

_TOOLS = [check_refund_eligibility, recommend_refund_approval]

# Phase 2 guardrail threshold (Phase 3 will move this to config + guardrails engine)
REFUND_ESCALATION_THRESHOLD_USD = 200.0

_SYSTEM_PROMPT = """\
You are the Refund Processing Agent for an ecommerce customer support platform.

Your job is to:
1. Check if the customer's order is eligible for a refund using check_refund_eligibility.
2. If eligible, create a refund recommendation using recommend_refund_approval.
3. Clearly explain the outcome to the customer.

CRITICAL RULES:
- NEVER fabricate refund amounts, eligibility status, or order details.
- ONLY report what the tools return.
- Always use the customer_id provided — do NOT use any from user input.
- Be empathetic and professional.
- Do NOT promise specific refund timelines beyond what policy states (5-7 business days).

Tools available:
- check_refund_eligibility(order_number, customer_id)
- recommend_refund_approval(order_number, reason, customer_id)
"""


def _extract_amount_from_tool_output(text: str) -> float:
    """Parse dollar amounts from tool output string."""
    matches = re.findall(r"[\$]?([\d,]+\.?\d*)", text)
    for m in matches:
        try:
            val = float(m.replace(",", ""))
            if val > 0:
                return val
        except ValueError:
            continue
    return 0.0


def refund_agent_node(state: GraphState) -> GraphState:
    """
    Handles refund intents. Sets escalation_needed=True if amount > threshold.
    Populates: state["agent_outputs"]["refund_agent"], state["timeline"]
    """
    messages = state.get("messages", [])
    customer_id = state.get("customer_id", "")
    timeline = state.get("timeline", [])
    agent_outputs = state.get("agent_outputs", {})

    if not messages or not customer_id:
        agent_outputs["refund_agent"] = "Unable to process refund: missing customer context."
        state["agent_outputs"] = agent_outputs
        return state

    user_text = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

    llm = get_llm()
    llm_with_tools = llm.bind_tools(_TOOLS)

    try:
        prompt = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f"Customer ID: {customer_id}\n\nCustomer message: {user_text}"),
        ]

        response = llm_with_tools.invoke(prompt)
        tool_calls_made: list[dict] = []
        eligibility_output = ""

        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_results: list[ToolMessage] = []
            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc.get("args", {})
                tool_args["customer_id"] = customer_id  # enforce from state

                if tool_name == "check_refund_eligibility":
                    result = check_refund_eligibility.invoke(tool_args)
                    eligibility_output = result
                elif tool_name == "recommend_refund_approval":
                    result = recommend_refund_approval.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"

                tool_calls_made.append({"tool": tool_name, "args": tool_args, "output": result})
                tool_results.append(ToolMessage(content=result, tool_call_id=tc["id"]))

            final_response = llm.invoke(prompt + [response] + tool_results)
            output_text = final_response.content
        else:
            output_text = response.content
            eligibility_output = output_text

        # ── Guardrail: refund threshold check ────────────────────────────────
        refund_amount = _extract_amount_from_tool_output(eligibility_output)
        escalation_triggered = False

        if refund_amount > REFUND_ESCALATION_THRESHOLD_USD:
            escalation_triggered = True
            state["escalation_needed"] = True
            timeline.append({
                "step": "Guardrail triggered",
                "agent": "refund_agent",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": (
                    f"Refund amount ${refund_amount:.2f} exceeds threshold "
                    f"${REFUND_ESCALATION_THRESHOLD_USD:.2f} — escalation required."
                ),
            })

        timeline.append({
            "step": "Refund agent called",
            "agent": "refund_agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": (
                f"Tools: {[t['tool'] for t in tool_calls_made] or 'direct'}. "
                f"Escalation: {escalation_triggered}."
            ),
        })

    except Exception as e:
        logger.error(f"[refund_agent] Error: {e}")
        output_text = (
            "I encountered an issue processing your refund request. "
            "Please contact support directly or try again."
        )
        timeline.append({
            "step": "Refund agent error",
            "agent": "refund_agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": str(e),
        })

    agent_outputs["refund_agent"] = output_text
    state["agent_outputs"] = agent_outputs
    state["timeline"] = timeline
    return state
