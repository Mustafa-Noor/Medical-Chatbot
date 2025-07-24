import os
import sys
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Setup for importing config if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.config import settings

# ---- CONFIG ---- #
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#FAISS_BASE_DIR = settings.CSV_EMBEDDINGS_DIR
RELEVANCE_THRESHOLD = 0.8  # Lower score = better match

def list_available_topics():
    return [d for d in os.listdir(FAISS_BASE_DIR) if os.path.isdir(os.path.join(FAISS_BASE_DIR, d))]

def load_vector_store(topic: str):
    vector_path = os.path.join(FAISS_BASE_DIR, topic)
    return FAISS.load_local(vector_path, EMBEDDING_MODEL, allow_dangerous_deserialization=True)

def search_topic(db: FAISS, query: str, top_k: int = 5):
    results = db.similarity_search_with_score(query, k=top_k)
    filtered = [r for r in results if r[1] <= RELEVANCE_THRESHOLD]

    if not filtered:
        print("\n⚠️ No relevant matches found.")
        return

    print("\n🔎 Top Results (Lower Score = Better Match):")
    for i, (doc, score) in enumerate(filtered, 1):
        print(f"\n--- Result {i} ---")
        print(doc.page_content)
        print(f"[📚 Source: {doc.metadata.get('source', 'Unknown')}]")
        print(f"[📊 Score: {score:.4f}]")

def main():
    print("📚 Available Topics:\n")
    topics = list_available_topics()
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")

    choice = input("\nEnter topic number to search: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(topics)):
        print("❌ Invalid choice.")
        return

    topic_name = topics[int(choice) - 1]
    print(f"\n✅ Loading FAISS index for: {topic_name}")
    db = load_vector_store(topic_name)

    while True:
        query = input("\n📝 Enter your query (or type 'exit' to quit): ").strip()
        if query.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        search_topic(db, query)

if __name__ == "__main__":
    main()
