from app.utils.llm import call_llm  # import your LLM wrapper

def generate_response(query: str, context: str = ""):
    prompt = f"Answer the following based on context:\n\n{context}\n\nQuestion: {query}"
    return call_llm(prompt)
