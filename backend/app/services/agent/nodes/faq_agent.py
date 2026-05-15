"""
FAQ Agent Node

Answers policy/knowledge-base questions using DB retrieval.
Phase 3 will upgrade this to FAISS RAG pipeline.
"""
from datetime import datetime, timezone
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from app.services.agent.state import GraphState
from app.services.agent.llm import get_llm
from app.services.agent.tools.faq import get_faq_answer
import logging

logger = logging.getLogger(__name__)

_TOOLS = [get_faq_answer]

_SYSTEM_PROMPT = """\
You are the FAQ Agent for an ecommerce customer support platform.

Your job is to answer customer questions about policies, processes, and general information
by retrieving relevant documents from the knowledge base.

CRITICAL RULES:
- ALWAYS use the get_faq_answer tool first to retrieve policy content.
- NEVER invent policy details, timelines, or amounts not present in the retrieved content.
- If the tool returns no relevant document, honestly say you don't have that specific information
  and suggest the customer contact support.
- Summarise the retrieved content clearly and concisely for the customer.
- Do not quote entire documents — extract the relevant answer for their question.
- Be friendly and helpful.

Tool available:
- get_faq_answer(query): searches the knowledge base for relevant policy documents
"""


def faq_agent_node(state: GraphState) -> GraphState:
    """
    Handles FAQ/policy intents via DB knowledge retrieval.
    Populates: state["agent_outputs"]["faq_agent"], state["timeline"]
    """
    messages = state.get("messages", [])
    timeline = state.get("timeline", [])
    agent_outputs = state.get("agent_outputs", {})

    if not messages:
        agent_outputs["faq_agent"] = "No question provided."
        state["agent_outputs"] = agent_outputs
        return state

    user_text = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

    llm = get_llm()
    llm_with_tools = llm.bind_tools(_TOOLS)

    try:
        prompt = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_text),
        ]

        response = llm_with_tools.invoke(prompt)
        retrieved_source = ""

        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_results: list[ToolMessage] = []
            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc.get("args", {})

                if tool_name == "get_faq_answer":
                    result = get_faq_answer.invoke(tool_args)
                    retrieved_source = result
                else:
                    result = f"Unknown tool: {tool_name}"

                tool_results.append(ToolMessage(content=result, tool_call_id=tc["id"]))

            final_response = llm.invoke(prompt + [response] + tool_results)
            output_text = final_response.content
        else:
            # LLM answered directly without tool — acceptable for simple greetings within FAQ
            output_text = response.content

        timeline.append({
            "step": "FAQ agent called",
            "agent": "faq_agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": (
                f"Retrieved {len(retrieved_source)} chars from knowledge base. "
                "Phase 3 will upgrade to FAISS vector retrieval."
            ),
        })

    except Exception as e:
        logger.error(f"[faq_agent] Error: {e}")
        output_text = (
            "I'm sorry, I had trouble retrieving the relevant policy information. "
            "Please contact our support team for detailed assistance."
        )
        timeline.append({
            "step": "FAQ agent error",
            "agent": "faq_agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": str(e),
        })

    agent_outputs["faq_agent"] = output_text
    state["agent_outputs"] = agent_outputs
    state["timeline"] = timeline
    return state
