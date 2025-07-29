# import os
# import sys
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain.schema import Document

# # Load config
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# from app.config import settings

# # ---- CONFIG ---- #
# EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# FAISS_BASE_DIR = settings.CSV_EMBEDDINGS_DIR  # Make sure this is defined in your settings
# RELEVANCE_THRESHOLD = 0.9  # Lower is more relevant


# def list_available_topics():
#     """List all available FAISS folders (topics)."""
#     return [d for d in os.listdir(FAISS_BASE_DIR) if os.path.isdir(os.path.join(FAISS_BASE_DIR, d))]


# def load_vector_store(topic: str):
#     """Load a FAISS vector store for the given topic name."""
#     vector_path = os.path.join(FAISS_BASE_DIR, topic)
#     return FAISS.load_local(vector_path, EMBEDDING_MODEL, allow_dangerous_deserialization=True)


# # def search_csv(topic: str, query: str, k: int = 3):
# #     """
# #     Search a FAISS CSV vector store for a given query and topic.
    
# #     Returns:
# #         {
# #             "score": average_score,  # Between 0 (perfect) to 1+
# #             "docs": [ { "content": ..., "score": ..., "source": ... }, ... ]
# #         }
# #     """
# #     try:
# #         db = load_vector_store(topic)
# #         results = db.similarity_search_with_score(query, k=k)
# #         print("\n🔍 RAW FAISS RESULTS:")
# #         for i, (doc, score) in enumerate(results):
# #             print(f"{i+1}. Score: {score:.4f} | Text: {doc.page_content[:80]}...")

# #         if not results:
# #             return {"score": 0.0, "docs": []}

# #         # Filter by relevance threshold
# #         filtered = [r for r in results if r[1] <= RELEVANCE_THRESHOLD]
# #         if not filtered:
# #             return {"score": 0.0, "docs": []}

# #         avg_score = sum(1 - score for _, score in filtered) / len(filtered)

# #         docs = []
# #         for doc, score in filtered:
# #             docs.append(Document(
# #             page_content=doc.page_content,
# #             metadata={
# #                 "score": round(score, 4),
# #                 "topic": doc.metadata.get("topic", "Unknown"),
# #                 "subtopic": doc.metadata.get("subtopic", ""),
# #                 "question": doc.metadata.get("question", "")
# #             }))

# #         return {"score": round(avg_score, 4), "docs": docs}
    
# #     except Exception as e:
# #         print("Error in search_csv:", e)
# #         return {"score": 0.0, "docs": [], "error": str(e)}

# def search_csv(topic: str, query: str, k: int = 3):
#     """
#     Search a FAISS CSV vector store for a given query and topic.
#     Only returns results if the top result exactly matches the query string.
#     """
#     try:
#         vector_path = os.path.join(FAISS_BASE_DIR, topic)
#         print(f"\n🔍 [CSV Search] Query: {query}")
#         print(f"📘 Topic: {topic}")
#         print(f"📁 Loading FAISS index from: {vector_path}")

#         db = FAISS.load_local(vector_path, EMBEDDING_MODEL, allow_dangerous_deserialization=True)
#         results = db.similarity_search_with_score(query, k=k)

#         if not results:
#             print("⚠️ No results returned.")
#             return {"score": 0.0, "docs": []}

#         print("📊 Top-k Results:")
#         for i, (doc, score) in enumerate(results):
#             print(f"  {i+1}. Score: {score:.4f} | Snippet: {doc.page_content[:80]}...")

#         # Check exact match on top document
#         top_doc, top_score = results[0]
#         top_question = top_doc.metadata.get("question", "").strip().lower()
#         if top_question != query.strip().lower():
#             print("❌ Top result is not an exact match. Skipping CSV.")
#             return {"score": 0.0, "docs": []}

#         # Continue if exact match
#         filtered = [r for r in results if r[1] <= RELEVANCE_THRESHOLD]
#         print(f"✅ Filtered Results (≤ {RELEVANCE_THRESHOLD}): {len(filtered)}")

#         avg_score = sum(1 - score for _, score in filtered) / len(filtered)

#         docs = [
#             Document(
#                 page_content=doc.page_content,
#                 metadata={
#                     "score": round(score, 4),
#                     "topic": doc.metadata.get("topic", "Unknown"),
#                     "subtopic": doc.metadata.get("subtopic", ""),
#                     "question": doc.metadata.get("question", "")
#                 }
#             )
#             for doc, score in filtered
#         ]

#         print(f"📈 Average Filtered Score: {avg_score:.4f}")
#         return {"score": round(avg_score, 4), "docs": docs}

#     except Exception as e:
#         print(f"❌ Error in search_csv: {e}")
#         return {"score": 0.0, "docs": [], "error": str(e)}




# # res = search_csv("Paediatrics", "What is chromosomes?")
# # print(res) 


import os
import sys
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Load config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.config import settings

# ---- CONFIG ---- #
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
RELEVANCE_THRESHOLD = 0.9
QDRANT_COLLECTION_SUFFIX = "csv"

client = QdrantClient(
    url=settings.Qdrant_url,
    api_key=settings.Qdrant_key,
)


def list_available_topics():
    """List all Qdrant collections that end with 'csv'."""
    collections = client.get_collections().collections
    return [col.name for col in collections if col.name.endswith(QDRANT_COLLECTION_SUFFIX)]


def load_vector_store(topic: str):
    """Load Qdrant vector store for a specific collection (topic)."""
    return Qdrant(
        client=client,
        collection_name=topic,
        embeddings=EMBEDDING_MODEL
    )


def search_csv(topic: str, query: str, k: int = 3):
    """
    Search a Qdrant CSV vector store for a given query and topic.
    Only returns results if the top result exactly matches the query string.
    """
    try:
        print(f"\n🔍 [CSV Search - Qdrant] Query: {query}")
        print(f"📘 Topic: {topic}")

        db = load_vector_store(topic)
        results = db.similarity_search_with_score(query, k=k)

        if not results:
            print("⚠️ No results returned.")
            return {"score": 0.0, "docs": []}

        print("📊 Top-k Results:")
        for i, (doc, score) in enumerate(results):
            print(f"  {i+1}. Score: {score:.4f} | Snippet: {doc.page_content[:80]}...")

        # Check exact match on top document
        top_doc, top_score = results[0]
        top_question = top_doc.metadata.get("question", "").strip().lower()
        if top_question != query.strip().lower():
            print("❌ Top result is not an exact match. Skipping CSV.")
            return {"score": 0.0, "docs": []}

        filtered = [r for r in results if r[1] <= RELEVANCE_THRESHOLD]
        print(f"✅ Filtered Results (≤ {RELEVANCE_THRESHOLD}): {len(filtered)}")

        avg_score = sum(1 - score for _, score in filtered) / len(filtered)

        docs = [
            Document(
                page_content=doc.page_content,
                metadata={
                    "score": round(score, 4),
                    "topic": doc.metadata.get("topic", "Unknown"),
                    "subtopic": doc.metadata.get("subtopic", ""),
                    "question": doc.metadata.get("question", "")
                }
            )
            for doc, score in filtered
        ]

        print(f"📈 Average Filtered Score: {avg_score:.4f}")
        return {"score": round(avg_score, 4), "docs": docs}

    except Exception as e:
        print(f"❌ Error in search_csv: {e}")
        return {"score": 0.0, "docs": [], "error": str(e)}