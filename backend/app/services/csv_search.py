import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_query_embedding(text: str):
    return model.encode(text)

def load_csv_index(topic: str):
    try:
        with open(f"data/csv_embeddings/{topic}_index.pkl", "rb") as f:
            index = pickle.load(f)
        with open(f"data/csv_embeddings/{topic}_qa.pkl", "rb") as f:
            qa_pairs = pickle.load(f)
        return index, qa_pairs
    except FileNotFoundError:
        return None, None

def search_csv(query: str, topic: str, threshold=0.5, top_k=3):
    query_vector = get_query_embedding(query)
    index, qa_pairs = load_csv_index(topic)
    if not index or not qa_pairs:
        return []

    distances, indices = index.search(np.array([query_vector]), top_k)
    results = [qa_pairs[i] for i in indices[0] if distances[0][i] < threshold]
    return results
