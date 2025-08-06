import os
from typing import List
import numpy as np
from langchain.schema import Document
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from app.config import settings

# --- Gemini Embeddings Setup --- #
genai.configure(api_key=settings.Google_key)
EMBEDDING_MODEL = "models/embedding-001"
SIMILARITY_THRESHOLD = 0.7  # Adjust this based on desired cutoff

# --- Qdrant Setup --- #
qdrant_client = QdrantClient(
    url=settings.Qdrant_url,
    api_key=settings.Qdrant_key,
)


# def embed_with_gemini(text: str) -> List[float]:
#     """Embed a string using Gemini embeddings."""
#     response = genai.embed_content(
#         model=EMBEDDING_MODEL,
#         content=text,
#         task_type="retrieval_query"
#     )
#     return response["embedding"]


def list_available_json_topics() -> List[str]:
    """List Qdrant collections (excluding -csv collections)."""
    collections = qdrant_client.get_collections().collections
    return [c.name for c in collections if not c.name.endswith("csv")]


def search_json(topic: str, query: str,query_vector: np.ndarray, k: int = 3):
    try:
        print(f"\n🔍 [QDRANT Search] Query: {query}")
        print(f"📘 Topic (Collection): {topic}")

        # Embed the query
        # query_vector = np.array(embed_with_gemini(query)).reshape(1, -1)

        # Fetch all vectors and payloads from the collection
        # points = qdrant_client.scroll(
        #     collection_name=topic,
        #     with_vectors=True,
        #     with_payload=True,
        #     limit=500  # adjust based on size
        # )[0]

        points = qdrant_client.search(
            collection_name=topic,
            query_vector=query_vector[0],
            limit=20,
            with_vectors=True,
            with_payload=True
        )

        vectors = []
        payloads = []
        for p in points:
            if p.vector is not None and p.payload is not None:
                vectors.append(p.vector)
                payloads.append(p.payload)

        if not vectors:
            print("⚠️ No vectors found in the collection.")
            return {"score": 0.0, "docs": []}

        # Compute cosine similarity
        vector_matrix = np.array(vectors)
        similarities = cosine_similarity(query_vector, vector_matrix)[0]

        # Pair with payloads and sort by similarity
        ranked = sorted(zip(payloads, similarities), key=lambda x: x[1], reverse=True)

        # Filter based on threshold
        filtered = [(payload, score) for payload, score in ranked if score >= SIMILARITY_THRESHOLD]
        print(f"✅ Filtered Results (≥ {SIMILARITY_THRESHOLD}): {len(filtered)}")

        if not filtered:
            print("⚠️ No relevant documents found.")
            return {"score": 0.0, "docs": []}

        avg_score = sum(score for _, score in filtered) / len(filtered)

        docs = [
            Document(
                page_content=payload.get("page_content", ""),
                metadata={
                    "similarity": round(score, 4),
                    "source": payload.get("source", "Unknown"),
                    **{k: v for k, v in payload.items() if k not in ("page_content", "source")}
                }
            )
            for payload, score in filtered[:k]
        ]

         # 🧠 Print snippets of top results
        print("\n🧠 Top Relevant Snippets:")
        for i, (payload, score) in enumerate(filtered[:k]):
            # Try multiple keys in fallback order
            content = (
                payload.get("page_content")
                or payload.get("text")
                or payload.get("content")
                or payload.get("chunk")
                or ""
            )
            snippet = content[:200].replace("\n", " ").strip()
            print(f"{i+1}. ({score:.4f}) {snippet if snippet else '[Empty snippet]'}...")

        print(f"\n📈 Average Similarity Score: {avg_score:.4f}")
        return {"score": round(avg_score, 4), "docs": docs}

    except Exception as e:
        print(f"❌ Error in search_json_cosine: {e}")
        return {"score": 0.0, "docs": [], "error": str(e)}



# res = search_json("5th_metatarsal_fracture", "what is the metatatarsal fracture?")
# print(res)