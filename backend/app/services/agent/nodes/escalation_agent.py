"""
Escalation Agent Node

Creates support tickets and escalation logs when human intervention is needed.
Triggers on: explicit escalation intent, low confidence, or guardrail violations.
"""
from datetime import datetime, timezone
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from app.services.agent.state import GraphState
from app.services.agent.llm import get_llm
from app.services.agent.tools.tickets import create_support_ticket
import logging

logger = logging.getLogger(__name__)

_TOOLS = [create_support_ticket]

_SYSTEM_PROMPT = """\
You are the Human Escalation Agent for an ecommerce customer support platform.

Your job is to create a support ticket for cases that require human review.
You must:
1. Understand the customer's issue from the conversation.
2. Create a clear, professional support ticket using create_support_ticket.
3. Reassure the customer that a human agent will help them.

Parameters for create_support_ticket:
- customer_id: (provided — do not change)
- subject: A clear, concise summary of the issue (max 100 chars)
- description: Detailed description of what the customer needs help with
- priority: Choose based on urgency — "low", "medium", "high", or "urgent"
  - urgent: threatening legal action, accusing fraud, payment issues
  - high: delayed orders, significant refunds, repeated failures
  - medium: general complaints, policy questions escalated
  - low: preference questions, minor issues
- session_id: (provided — do not change)
- escalation_reason: Why AI is escalating (be specific)

Be empathetic and professional. Tell the customer their ticket number after creation.
"""


def escalation_agent_node(state: GraphState) -> GraphState:
    """
    Creates a support ticket when escalation is needed.
    Only runs if state["escalation_needed"] = True or "escalation" in intents.
    Populates: state["agent_outputs"]["escalation_agent"], state["timeline"]
    """
    messages = state.get("messages", [])
    customer_id = state.get("customer_id", "")
    session_id = state.get("session_id", "unknown")
    timeline = state.get("timeline", [])
    agent_outputs = state.get("agent_outputs", {})
    intents = state.get("intents", [])
    confidence = state.get("confidence_score", 1.0)

    # Build escalation reason from context
    escalation_reasons: list[str] = []
    if "escalation" in intents:
        escalation_reasons.append("Customer explicitly requested human agent.")
    if state.get("escalation_needed"):
        escalation_reasons.append("Guardrail triggered (refund threshold exceeded or confidence too low).")
    if confidence < 0.5:
        escalation_reasons.append(f"Low AI confidence score: {confidence:.2f}.")
    if not escalation_reasons:
        escalation_reasons.append("Escalation requested by orchestrator.")

    escalation_reason_str = " ".join(escalation_reasons)

    if not messages or not customer_id:
        agent_outputs["escalation_agent"] = (
            "I'm connecting you with a human support agent. "
            "Please wait — a representative will be in touch soon."
        )
        timeline.append({
            "step": "Escalation triggered (no ticket — missing context)",
            "agent": "escalation_agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": escalation_reason_str,
        })
        state["agent_outputs"] = agent_outputs
        state["timeline"] = timeline
        return state

    user_text = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

    llm = get_llm()
    llm_with_tools = llm.bind_tools(_TOOLS)

    try:
        prompt = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Customer ID: {customer_id}\n"
                    f"Session ID: {session_id}\n"
                    f"Escalation reason: {escalation_reason_str}\n\n"
                    f"Customer message: {user_text}"
                )
            ),
        ]

        response = llm_with_tools.invoke(prompt)
        output_text = ""
        ticket_created = False

        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_results: list[ToolMessage] = []
            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc.get("args", {})

                # Enforce IDs from state — never from LLM
                tool_args["customer_id"] = customer_id
                tool_args["session_id"] = session_id

                if tool_name == "create_support_ticket":
                    result = create_support_ticket.invoke(tool_args)
                    ticket_created = True
                else:
                    result = f"Unknown tool: {tool_name}"

                tool_results.append(ToolMessage(content=result, tool_call_id=tc["id"]))

            final_response = llm.invoke(prompt + [response] + tool_results)
            output_text = final_response.content
        else:
            output_text = response.content

        timeline.append({
            "step": "Escalated to human agent",
            "agent": "escalation_agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": f"Ticket created: {ticket_created}. Reason: {escalation_reason_str}",
        })

    except Exception as e:
        logger.error(f"[escalation_agent] Error: {e}")
        output_text = (
            "I've flagged your case for human review. "
            "A support representative will contact you within 24 hours."
        )
        timeline.append({
            "step": "Escalation agent error",
            "agent": "escalation_agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": str(e),
        })

    agent_outputs["escalation_agent"] = output_text
    state["agent_outputs"] = agent_outputs
    state["timeline"] = timeline
    return state
