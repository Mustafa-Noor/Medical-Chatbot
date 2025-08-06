import os
import sys
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain.schema import Document
from qdrant_client import QdrantClient
import google.generativeai as genai
import logging
logger = logging.getLogger()

# ---- PATH SETUP ---- #
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.config import settings  # Make sure this exists

# ---- CONFIG ---- #
genai.configure(api_key=settings.Google_key)
EMBEDDING_MODEL = "models/embedding-001"
SIMILARITY_THRESHOLD = 0.7
QDRANT_COLLECTION_SUFFIX = "csv"

qdrant_client = QdrantClient(
    url=settings.Qdrant_url,
    api_key=settings.Qdrant_key,
)


# def embed_with_gemini(text: str) -> List[float]:
#     """Generate Gemini embeddings for a query."""
#     response = genai.embed_content(
#         model=EMBEDDING_MODEL,
#         content=text,
#         task_type="retrieval_query"
#     )
#     return response["embedding"]


def list_available_csv_topics() -> List[str]:
    """List all Qdrant collections ending in 'csv'."""
    collections = qdrant_client.get_collections().collections
    return [col.name for col in collections if col.name.endswith(QDRANT_COLLECTION_SUFFIX)]


def search_csv(topic: str, query: str, query_vector: np.ndarray, k: int = 3) -> Dict[str, Any]:
    topic = topic.strip() + "_csv"
    query_normalized = query.strip().lower()

    try:
        print(f"\n🔍 [QDRANT CSV Search] Query: {query}")
        print(f"📘 Topic: {topic}")

        logger.info("query vector start")
        # # Embed query
        # query_vector = np.array(embed_with_gemini(query)).reshape(1, -1)

        logger.info("query vector end------")
        # Fetch points from Qdrant
        # points = qdrant_client.scroll(
        #     collection_name=topic,
        #     with_vectors=True,
        #     with_payload=True,
        #     limit=500
        # )[0]

        points = qdrant_client.search(
            collection_name=topic,
            query_vector=query_vector[0],
            limit=20,
            with_vectors=True,
            with_payload=True
        )

        vectors, payloads = [], []
        for p in points:
            if p.vector is not None and p.payload is not None:
                vectors.append(p.vector)
                payloads.append(p.payload)

        if not vectors:
            print("⚠️ No vectors found.")
            return {"score": 0.0, "docs": []}

        
        # Similarity
        vector_matrix = np.array(vectors)
        logger.info("cosine similarirty")
        similarities = cosine_similarity(query_vector, vector_matrix)[0]
        logger.info("simi end------")
        ranked = sorted(zip(payloads, similarities), key=lambda x: x[1], reverse=True)

        # Filter
        filtered = [(payload, score) for payload, score in ranked if score >= SIMILARITY_THRESHOLD]
        print(f"✅ Filtered Results (≥ {SIMILARITY_THRESHOLD}): {len(filtered)}")

        if not filtered:
            print("⚠️ No relevant documents found.")
            return {"score": 0.0, "docs": []}

        # Average score
        avg_score = sum(score for _, score in filtered) / len(filtered)

        docs = []
        for payload, score in filtered[:k]:
            page_content = (
                payload.get("page_content")
                or payload.get("text")
                or payload.get("content")
                or payload.get("chunk")
                or ""
            )
            if page_content.strip():
                docs.append(Document(
                    page_content=page_content.strip(),
                    metadata={
                        "similarity": round(score, 4),
                        "question": payload.get("question", ""),
                        "topic": payload.get("topic", "Unknown"),
                        "subtopic": payload.get("subtopic", "")
                    }
                ))

        print("\n🧠 Top Relevant Snippets:")
        for i, (payload, score) in enumerate(filtered[:k]):
            content = payload.get("page_content") or payload.get("question") or ""
            snippet = content[:200].replace("\n", " ").strip()
            print(f"{i+1}. ({score:.4f}) {snippet if snippet else '[Empty snippet]'}...")

        print(f"\n📈 Average Similarity Score: {avg_score:.4f}")
        return {"score": round(avg_score, 4), "docs": docs}

    except Exception as e:
        print(f"❌ Error in search_csv: {e}")
        return {"score": 0.0, "docs": [], "error": str(e)}


# Example call
# res = search_csv("5th_metatarsal_fracture", "What happens if the fracture fails to heal?")
# print(res)
