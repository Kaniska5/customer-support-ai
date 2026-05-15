from langchain_core.tools import tool
from app.database.vector_store import faq_vector_store
import logging

logger = logging.getLogger(__name__)

@tool
def get_faq_answer(query: str) -> str:
    """
    Search the FAQ knowledge base for documents matching the customer's query.
    Uses semantic vector search via FAISS (Phase 3 RAG).

    Args:
        query: The customer's question or topic to search for.

    Returns:
        Relevant FAQ content, or a message indicating no match was found.
    """
    try:
        # Perform similarity search retrieving top 3 closest chunks
        docs = faq_vector_store.similarity_search(query, k=3)
        
        if not docs:
            return (
                "I could not find a specific policy document for your question. "
                "Please contact our support team directly for detailed assistance."
            )
            
        # Compose response
        parts: list[str] = []
        for doc in docs:
            title = doc.metadata.get("title", "Policy")
            parts.append(f"**{title}**\n{doc.page_content}")
            
        return "\n\n---\n\n".join(parts)
        
    except Exception as e:
        logger.error(f"Error during FAISS similarity search: {e}")
        return "An error occurred while retrieving FAQ documents. Please try again later."

