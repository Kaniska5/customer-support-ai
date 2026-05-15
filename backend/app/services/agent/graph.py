"""
LangGraph Agent Pipeline — Graph Compilation

Wires all agent nodes into a stateful StateGraph.

Flow:
  START → analyzer → [order_agent?, refund_agent?, faq_agent?] → escalation_agent? → synthesizer → END

Routing logic:
- analyzer detects intents and sets state["intents"]
- conditional_router dispatches to one or more specialist agents
- escalation_router checks state["escalation_needed"] after agents run
- synthesizer always runs last

Multi-intent support:
- A single message can trigger multiple agents (e.g., order_tracking + refund_request)
- This is handled by sequential routing through the intent list in the state.
"""
from langgraph.graph import StateGraph, END, START
from app.services.agent.state import GraphState
from app.services.agent.nodes.analyzer import analyzer_node
from app.services.agent.nodes.order_agent import order_agent_node
from app.services.agent.nodes.refund_agent import refund_agent_node
from app.services.agent.nodes.faq_agent import faq_agent_node
from app.services.agent.nodes.escalation_agent import escalation_agent_node
from app.services.agent.nodes.synthesizer import synthesizer_node
from typing import Literal
import logging

logger = logging.getLogger(__name__)

# Maximum number of agent hops to prevent infinite loops
MAX_AGENT_HOPS = 5


def should_run_order_agent(state: GraphState) -> bool:
    return "order_tracking" in state.get("intents", [])


def should_run_refund_agent(state: GraphState) -> bool:
    return "refund_request" in state.get("intents", [])


def should_run_faq_agent(state: GraphState) -> bool:
    return "faq" in state.get("intents", [])


def should_escalate(state: GraphState) -> bool:
    return (
        state.get("escalation_needed", False)
        or "escalation" in state.get("intents", [])
        or state.get("confidence_score", 1.0) < 0.45
    )


def _check_hop_limit(state: GraphState) -> GraphState:
    """Safety: cap total timeline steps to prevent runaway loops."""
    timeline = state.get("timeline", [])
    agent_steps = [t for t in timeline if t.get("agent") not in ("orchestrator", "synthesizer")]
    if len(agent_steps) >= MAX_AGENT_HOPS:
        logger.warning("[graph] MAX_AGENT_HOPS reached — forcing synthesizer.")
        state["escalation_needed"] = True
    return state


# ── Conditional edge functions ─────────────────────────────────────────────────

def route_from_analyzer(
    state: GraphState,
) -> list[str]:
    """
    Returns the list of next nodes to visit after the analyzer.
    LangGraph supports returning a list to fan out to multiple nodes.
    """
    next_nodes: list[str] = []

    if should_run_order_agent(state):
        next_nodes.append("order_agent")

    if should_run_refund_agent(state):
        next_nodes.append("refund_agent")

    if should_run_faq_agent(state):
        next_nodes.append("faq_agent")

    # If no specialist matched, go straight to synthesizer (handles general/escalation)
    if not next_nodes:
        next_nodes.append("synthesizer")

    return next_nodes


def route_to_escalation_or_synthesizer(
    state: GraphState,
) -> Literal["escalation_agent", "synthesizer"]:
    """After specialist agents run, decide if we need escalation."""
    _check_hop_limit(state)
    if should_escalate(state):
        return "escalation_agent"
    return "synthesizer"


# ── Build and compile the graph ────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)

    # Register nodes
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("order_agent", order_agent_node)
    graph.add_node("refund_agent", refund_agent_node)
    graph.add_node("faq_agent", faq_agent_node)
    graph.add_node("escalation_agent", escalation_agent_node)
    graph.add_node("synthesizer", synthesizer_node)

    # Entry point
    graph.add_edge(START, "analyzer")

    # Fan-out from analyzer to specialist agents (or directly to synthesizer)
    graph.add_conditional_edges(
        "analyzer",
        route_from_analyzer,
        {
            "order_agent": "order_agent",
            "refund_agent": "refund_agent",
            "faq_agent": "faq_agent",
            "synthesizer": "synthesizer",
        },
    )

    # Fan-in: after each specialist agent, decide escalation or synthesize
    for agent in ("order_agent", "refund_agent", "faq_agent"):
        graph.add_conditional_edges(
            agent,
            route_to_escalation_or_synthesizer,
            {
                "escalation_agent": "escalation_agent",
                "synthesizer": "synthesizer",
            },
        )

    # After escalation, always synthesize
    graph.add_edge("escalation_agent", "synthesizer")

    # Synthesizer always terminates
    graph.add_edge("synthesizer", END)

    return graph


# Singleton compiled graph — import this in the API layer
compiled_graph = build_graph().compile()
logger.info("[graph] LangGraph agent pipeline compiled successfully.")
