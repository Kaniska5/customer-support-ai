from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def get_llm():
    """
    Returns the primary LLM (Gemini 1.5 Pro) with OpenAI GPT-4o as fallback.
    Uses LangChain's native with_fallbacks for transparent failover.
    Compatible with langchain-google-genai>=4.x and langchain-openai>=1.x
    """
    primary_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.2,
        google_api_key=settings.GEMINI_API_KEY or None,
        max_retries=2,
    )

    fallback_llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        api_key=settings.OPENAI_API_KEY or None,
        max_retries=2,
    )

    # Transparent failover: if Gemini fails (quota/key error), OpenAI takes over
    return primary_llm.with_fallbacks([fallback_llm])

