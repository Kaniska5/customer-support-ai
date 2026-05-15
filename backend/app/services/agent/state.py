from typing import TypedDict, Optional, Any
from langchain_core.messages import BaseMessage


class GraphState(TypedDict, total=False):
    """
    Represents the full state of the LangGraph multi-agent conversation.
    Using total=False so LangGraph can do partial state updates cleanly.
    Required fields are explicitly initialized in the graph entry point.
    """
    # ── Identity ─────────────────────────────────────────────────────────────
    session_id: str
    customer_id: str
    ticket_id: Optional[str]          # linked support ticket (if any)

    # ── Conversation ─────────────────────────────────────────────────────────
    messages: list[BaseMessage]       # full conversation history

    # ── Intent detection (set by analyzer) ───────────────────────────────────
    intents: list[str]                # e.g. ["order_tracking", "refund_request"]
    confidence_score: float           # 0.0 – 1.0

    # ── Agent outputs (accumulated as agents run) ─────────────────────────────
    agent_outputs: dict[str, Any]     # {"order_agent": "...", "refund_agent": "..."}

    # ── Escalation ────────────────────────────────────────────────────────────
    escalation_needed: bool

    # ── Audit trail (append-only list of step dicts) ─────────────────────────
    # Format: [{"step": str, "agent": str, "timestamp": str, "details": str}]
    timeline: list[dict[str, Any]]

    # ── Final synthesised response ────────────────────────────────────────────
    final_response: str

