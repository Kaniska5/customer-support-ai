"""
Analyzer Node — Intent Classification

Classifies the customer's message into one or more intents and scores confidence.
This is always the first node in the LangGraph pipeline.
"""
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.agent.state import GraphState
from app.services.agent.llm import get_llm
import json
import logging

logger = logging.getLogger(__name__)

# Supported intent labels
VALID_INTENTS = {
    "order_tracking",
    "refund_request",
    "faq",
    "escalation",
    "general",
}

_SYSTEM_PROMPT = """\
You are an intent classifier for an ecommerce customer support system.
Analyze the customer message and return a JSON object with exactly these fields:
{
  "intents": ["<intent1>", "<intent2>"],
  "confidence_score": <float between 0.0 and 1.0>,
  "reasoning": "<one sentence explaining your classification>"
}

Valid intent labels (use only these, can return multiple):
- order_tracking   → asking about order status, shipping, tracking, delivery
- refund_request   → asking for refund, money back, return
- faq              → asking about policies, how things work, general information
- escalation       → requesting human agent, expressing extreme frustration, legal threats
- general          → greetings, thanks, other

Rules:
- Always return valid JSON only. No extra text.
- Use multiple intents if the message contains multiple topics.
- confidence_score reflects how certain you are (1.0 = very certain, 0.5 = ambiguous).
- If confidence is below 0.5, include "escalation" in intents.
"""


def analyzer_node(state: GraphState) -> GraphState:
    """
    Classifies intents and confidence from the latest user message.
    Populates: state["intents"], state["confidence_score"], state["timeline"]
    """
    messages = state.get("messages", [])
    if not messages:
        state["intents"] = ["general"]
        state["confidence_score"] = 0.5
        state["timeline"] = state.get("timeline", [])
        return state

    # Extract latest user message text
    latest = messages[-1]
    user_text = latest.content if hasattr(latest, "content") else str(latest)

    llm = get_llm()
    prompt_messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=user_text),
    ]

    try:
        response = llm.invoke(prompt_messages)
        raw = response.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        parsed = json.loads(raw)

        intents: list[str] = [
            i for i in parsed.get("intents", ["general"]) if i in VALID_INTENTS
        ]
        if not intents:
            intents = ["general"]

        confidence: float = float(parsed.get("confidence_score", 0.7))
        confidence = max(0.0, min(1.0, confidence))
        reasoning: str = parsed.get("reasoning", "Intent classified by analyzer.")

        # Low confidence → force escalation intent
        if confidence < 0.5 and "escalation" not in intents:
            intents.append("escalation")

    except Exception as e:
        logger.warning(f"[analyzer] LLM parse failed: {e}. Using fallback.")
        intents = ["general"]
        confidence = 0.5
        reasoning = "Fallback classification due to LLM parse error."

    timeline = state.get("timeline", [])
    timeline.append({
        "step": "Intent detected",
        "agent": "orchestrator",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": f"intents={intents}, confidence={confidence:.2f}. {reasoning}",
    })

    state["intents"] = intents
    state["confidence_score"] = confidence
    state["timeline"] = timeline
    return state
