from fastapi import APIRouter, Request
from app.services.csv_search import search_csv
from app.services.rag_pipeline import search_json_rag
from app.services.llm_fallback import call_fallback_llm

router = APIRouter()

@router.post("/chat")
async def handle_chat(request: Request):
    body = await request.json()
    query = body.get("query")
    topic = body.get("topic")

    if not query or not topic:
        return {"error": "Query and topic are required"}

    # Step 1: Search CSV
    csv_results = search_csv(query, topic)
    if csv_results:
        return {
            "source": "csv",
            "answer": csv_results[0]["answer"]
        }

    # Step 2: Search JSON with RAG
    json_result = search_json_rag(query, topic)
    if json_result:
        return {
            "source": "json_rag",
            "answer": json_result
        }

    # Step 3: Fallback to LLM
    llm_response = call_fallback_llm(query, topic)
    return {
        "source": "llm_fallback",
        "answer": llm_response
    }
