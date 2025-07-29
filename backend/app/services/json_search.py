import os
import sys
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.schema import Document
from qdrant_client import QdrantClient

# Load config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.config import settings

# ---- CONFIG ---- #
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
RELEVANCE_THRESHOLD = 1.2

# Qdrant client setup
qdrant_client = QdrantClient(
    url=settings.Qdrant_url,
    api_key=settings.Qdrant_key,
)


def list_available_json_topics() -> List[str]:
    """List available Qdrant collections (ignoring -csv collections)."""
    collections = qdrant_client.get_collections().collections
    return [c.name for c in collections if not c.name.endswith("csv")]


def load_json_vector_store(topic: str):
    """Load a Qdrant vector store for the given topic."""
    return Qdrant(
        client=qdrant_client,
        collection_name=topic,
        embeddings=EMBEDDING_MODEL,
    )


def search_json(topic: str, query: str, k: int = 3):
    try:
        print(f"\n🔍 [QDRANT Search] Query: {query}")
        print(f"📘 Topic (Collection): {topic}")

        db = Qdrant(
            client=qdrant_client,
            collection_name=topic,
            embeddings=EMBEDDING_MODEL,
        )

        results = db.similarity_search_with_score(query, k=k)

        if not results:
            print("⚠️ No results returned.")
            return {"score": 0.0, "docs": []}

        print("📊 Top-k Results:")
        for i, (doc, score) in enumerate(results):
            print(f"  {i+1}. Score: {score:.4f} | Snippet: {doc.page_content[:80]}...")

        filtered = [r for r in results if r[1] <= RELEVANCE_THRESHOLD]
        print(f"✅ Filtered Results (≤ {RELEVANCE_THRESHOLD}): {len(filtered)}")

        if not filtered:
            print("⚠️ All results above relevance threshold.")
            return {"score": 0.0, "docs": []}

        avg_score = sum(1 - score for _, score in filtered) / len(filtered)

        docs = [
            Document(
                page_content=doc.page_content,
                metadata={
                    "score": round(score, 4),
                    "source": doc.metadata.get("source", "Unknown")
                }
            )
            for doc, score in filtered
        ]

        print(f"📈 Average Filtered Score: {avg_score:.4f}")
        return {"score": round(avg_score, 4), "docs": docs}

    except Exception as e:
        print(f"❌ Error in search_json: {e}")
        return {"score": 0.0, "docs": [], "error": str(e)}



# res = search_json("Paediatrics", "what is chromosomes?")
# print(res)
