import requests

def call_fallback_llm(query: str, topic: str):
    prompt = f"You are a helpful medical assistant. Topic: {topic}\n\nQuestion: {query}\nAnswer:"
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer YOUR_GROQ_API_KEY",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-r1-distill-llama-70b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("LLM error:", e)
        return "Sorry, something went wrong with the assistant."
