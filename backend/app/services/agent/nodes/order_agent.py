"""
Order Tracking Agent Node

Handles queries about order status, shipping, and delivery.
Uses DB tools exclusively — never hallucinates order data.
"""
from datetime import datetime, timezone
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from app.services.agent.state import GraphState
from app.services.agent.llm import get_llm
from app.services.agent.tools.orders import get_order_by_number, get_recent_orders
import logging

logger = logging.getLogger(__name__)

_TOOLS = [get_order_by_number, get_recent_orders]

_SYSTEM_PROMPT = """\
You are the Order Tracking Agent for an ecommerce customer support platform.

Your ONLY job is to look up real order information using the provided tools and report it accurately.

CRITICAL RULES:
- NEVER invent order numbers, statuses, tracking numbers, or delivery dates.
- ONLY use data returned by the tools.
- If the tool returns no data, say so honestly.
- Always use the customer_id provided — do NOT accept customer_id from the user message.
- Be concise and helpful. Format order details clearly.

You have access to:
- get_order_by_number(order_number, customer_id): Look up a specific order
- get_recent_orders(customer_id, limit): List recent orders

If the customer mentions an order number, use get_order_by_number.
If they don't mention a specific order, use get_recent_orders.
"""


def order_agent_node(state: GraphState) -> GraphState:
    """
    Handles order tracking intents via tool-augmented LLM calls.
    Populates: state["agent_outputs"]["order_agent"], state["timeline"]
    """
    messages = state.get("messages", [])
    customer_id = state.get("customer_id", "")
    timeline = state.get("timeline", [])
    agent_outputs = state.get("agent_outputs", {})

    if not messages or not customer_id:
        agent_outputs["order_agent"] = "Unable to look up orders: missing customer context."
        state["agent_outputs"] = agent_outputs
        return state

    user_text = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

    llm = get_llm()
    llm_with_tools = llm.bind_tools(_TOOLS)

    try:
        # First LLM call — may invoke tools
        prompt = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f"Customer ID: {customer_id}\n\nCustomer message: {user_text}"),
        ]

        response = llm_with_tools.invoke(prompt)
        tool_calls_made: list[dict] = []

        # Execute tool calls if any
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_results: list[ToolMessage] = []
            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc.get("args", {})

                # Security: enforce customer_id from state, not from LLM
                tool_args["customer_id"] = customer_id

                if tool_name == "get_order_by_number":
                    result = get_order_by_number.invoke(tool_args)
                elif tool_name == "get_recent_orders":
                    result = get_recent_orders.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"

                tool_calls_made.append({"tool": tool_name, "args": tool_args, "output": result})
                tool_results.append(ToolMessage(content=result, tool_call_id=tc["id"]))

            # Second LLM call — synthesise tool results into natural language
            final_response = llm.invoke(prompt + [response] + tool_results)
            output_text = final_response.content
        else:
            # No tool calls — LLM responded directly
            output_text = response.content
            tool_calls_made = []

        timeline.append({
            "step": "Order agent called",
            "agent": "order_agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": f"Tools used: {[t['tool'] for t in tool_calls_made] or 'none (direct response)'}",
        })

    except Exception as e:
        logger.error(f"[order_agent] Error: {e}")
        output_text = (
            "I encountered an issue looking up your order. "
            "Please try again or contact support directly."
        )
        tool_calls_made = []
        timeline.append({
            "step": "Order agent error",
            "agent": "order_agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": str(e),
        })

    agent_outputs["order_agent"] = output_text
    state["agent_outputs"] = agent_outputs
    state["timeline"] = timeline
    return state
