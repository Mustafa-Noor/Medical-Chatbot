from app.pipelines.builder import build_graph
from app.schemas.search_state import SearchState

app_graph = build_graph()

def run_pipeline(query: str, topic: str, memory: str) -> dict:
    initial_state = SearchState(query=query, topic=topic, memory=memory)
    print("🧵 Initial SearchState:\n", initial_state.dict())
    print("🧠 Memory passed into initial state:\n", memory)

    final_state = app_graph.invoke(initial_state)

    if isinstance(final_state, dict):
        final_state = SearchState(**final_state)

    print("✅ DEBUG: Final Source =", final_state.source)
    print("✅ DEBUG: Final Answer =", final_state.final_answer[:80])

    return {
        "answer": final_state.final_answer or "No answer generated.",
        "source": final_state.source or "llm"
    }