import os
import sys
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

# Load config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.config import settings

# ---- CONFIG ---- #
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
FAISS_JSON_DIR = settings.JSON_EMBEDDINGS_DIR  # e.g., "embeddings/json/"
RELEVANCE_THRESHOLD = 0.9


def list_available_json_topics():
    """List available JSON-based FAISS folders (topics)."""
    return [d for d in os.listdir(FAISS_JSON_DIR) if os.path.isdir(os.path.join(FAISS_JSON_DIR, d))]


def load_json_vector_store(topic: str):
    """Load a FAISS vector store for the given JSON topic."""
    vector_path = os.path.join(FAISS_JSON_DIR, topic)
    return FAISS.load_local(vector_path, EMBEDDING_MODEL, allow_dangerous_deserialization=True)


def search_json(topic: str, query: str, k: int = 3):
    """
    Search a FAISS JSON vector store for a given query and topic.
    
    Returns:
        {
            "score": average_score,
            "docs": [ { "content": ..., "score": ..., "source": ... }, ... ]
        }
    """
    try:
        db = load_json_vector_store(topic)
        results = db.similarity_search_with_score(query, k=k)
        if not results:
            return {"score": 0.0, "docs": []}

        # Filter by relevance
        filtered = [r for r in results if r[1] <= RELEVANCE_THRESHOLD]
        if not filtered:
            return {"score": 0.0, "docs": []}

        avg_score = sum(1 - score for _, score in filtered) / len(filtered)

        docs = []
        for doc, score in filtered:
        #     docs.append({
        #         "content": doc.page_content,
        #         "score": round(score, 4),
        #         "source": doc.metadata.get("source", "Unknown")
        #     })

            docs.append(Document(
                page_content=doc.page_content,
                metadata={
                    "score": round(score, 4),
                    "source": doc.metadata.get("source", "Unknown")
                }
            ))


        return {"score": round(avg_score, 4), "docs": docs}
    
    except Exception as e:
        print("Error in search_json:", e)
        return {"score": 0.0, "docs": [], "error": str(e)}


# res = search_json("Paediatrics", "What is your name?")
# print(res)
