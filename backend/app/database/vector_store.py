import os
import logging
from typing import List, Dict, Any, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings

logger = logging.getLogger(__name__)

# We will save the FAISS index locally
INDEX_DIR = os.path.join(os.path.dirname(__file__), "../../../faiss_index")


def get_embeddings():
    """Return the configured embedding model using a local fast model."""
    # We use a fast, small, offline model to avoid API key requirements
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


class FAQVectorStore:
    """Wrapper for FAISS vector store management for FAQ documents."""

    def __init__(self):
        self.embeddings = get_embeddings()
        self.vector_store: Optional[FAISS] = None
        self._load_index()

    def _load_index(self):
        """Load the FAISS index from disk if it exists."""
        if os.path.exists(INDEX_DIR) and os.path.exists(os.path.join(INDEX_DIR, "index.faiss")):
            try:
                self.vector_store = FAISS.load_local(
                    INDEX_DIR, 
                    self.embeddings,
                    allow_dangerous_deserialization=True  # Safe since we generate it locally
                )
                logger.info(f"Loaded FAISS index from {INDEX_DIR}")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                self.vector_store = None
        else:
            logger.info("No existing FAISS index found. Will create a new one when documents are added.")

    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store and save to disk."""
        if not documents:
            return

        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)
            
        os.makedirs(INDEX_DIR, exist_ok=True)
        self.vector_store.save_local(INDEX_DIR)
        logger.info(f"Saved {len(documents)} documents to FAISS index at {INDEX_DIR}")

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """Perform similarity search for a query."""
        if not self.vector_store:
            logger.warning("FAISS index is not loaded. Returning empty results.")
            return []
        
        return self.vector_store.similarity_search(query, k=k)


# Singleton instance
faq_vector_store = FAQVectorStore()
