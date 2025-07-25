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
FAISS_BASE_DIR = settings.CSV_EMBEDDINGS_DIR  # Make sure this is defined in your settings
RELEVANCE_THRESHOLD = 0.9  # Lower is more relevant


def list_available_topics():
    """List all available FAISS folders (topics)."""
    return [d for d in os.listdir(FAISS_BASE_DIR) if os.path.isdir(os.path.join(FAISS_BASE_DIR, d))]


def load_vector_store(topic: str):
    """Load a FAISS vector store for the given topic name."""
    vector_path = os.path.join(FAISS_BASE_DIR, topic)
    return FAISS.load_local(vector_path, EMBEDDING_MODEL, allow_dangerous_deserialization=True)


def search_csv(topic: str, query: str, k: int = 3):
    """
    Search a FAISS CSV vector store for a given query and topic.
    
    Returns:
        {
            "score": average_score,  # Between 0 (perfect) to 1+
            "docs": [ { "content": ..., "score": ..., "source": ... }, ... ]
        }
    """
    try:
        db = load_vector_store(topic)
        results = db.similarity_search_with_score(query, k=k)
        print("\n🔍 RAW FAISS RESULTS:")
        for i, (doc, score) in enumerate(results):
            print(f"{i+1}. Score: {score:.4f} | Text: {doc.page_content[:80]}...")

        if not results:
            return {"score": 0.0, "docs": []}

        # Filter by relevance threshold
        filtered = [r for r in results if r[1] <= RELEVANCE_THRESHOLD]
        if not filtered:
            return {"score": 0.0, "docs": []}

        avg_score = sum(1 - score for _, score in filtered) / len(filtered)

        docs = []
        for doc, score in filtered:
            docs.append(Document(
            page_content=doc.page_content,
            metadata={
                "score": round(score, 4),
                "topic": doc.metadata.get("topic", "Unknown"),
                "subtopic": doc.metadata.get("subtopic", ""),
                "question": doc.metadata.get("question", "")
            }))

        return {"score": round(avg_score, 4), "docs": docs}
    
    except Exception as e:
        print("Error in search_csv:", e)
        return {"score": 0.0, "docs": [], "error": str(e)}


# res = search_csv("Paediatrics", "What is chromosomes?")
# print(res)