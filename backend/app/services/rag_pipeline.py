import json
from transformers import pipeline

qa_model = pipeline("question-answering", model="deepset/roberta-base-squad2")

def load_structured_json(topic: str):
    try:
        with open(f"data/structured_json/{topic}.json", "r") as f:
            data = json.load(f)
        return data.get("content", [])
    except FileNotFoundError:
        return []

def search_json_rag(query: str, topic: str):
    data = load_structured_json(topic)
    best_answer = ""
    best_score = 0.0

    for item in data:
        context = item.get("text", "")
        if not context.strip():
            continue
        result = qa_model(question=query, context=context)
        if result["score"] > best_score and result["score"] > 0.5:
            best_score = result["score"]
            best_answer = result["answer"]

    return best_answer if best_answer else None
