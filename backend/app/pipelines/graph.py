from langgraph.graph import StateGraph, END
from app.services.csv_search import search_csv
from app.services.json_search import search_json
from app.services.llm_context import generate_response
from app.schemas.search_state import SearchState


builder = StateGraph(SearchState)

# Node 1: CSV Search
def csv_node(state: SearchState) -> SearchState:
    result = search_csv(state.topic, state.query)
    state.csv_score = result["score"]
    state.csv_docs = result["docs"]
    return state

# Node 2: JSON RAG Search
def json_node(state: SearchState) -> SearchState:
    result = search_json(state.topic, state.query)
    state.json_score = result["score"]
    state.json_docs = result["docs"]
    return state

# Node 3: LLM Response Generator
def llm_node(state: SearchState) -> SearchState:
    context_docs = state.csv_docs if state.csv_docs else state.json_docs
    context = "\n\n".join([doc.page_content for doc in context_docs])
    answer = generate_response(state.query, context)
    state.final_answer = answer
    return state

# Conditional branching
def check_csv(state: SearchState) -> str:
    return "json" if state.csv_score is not None and state.csv_score < 0.5 else "llm"

def check_json(state: SearchState) -> str:
    return "llm" if state.json_score is not None and state.json_score < 0.8 else "direct"


# Build the graph
builder = StateGraph(SearchState)
builder.add_node("csv", csv_node)
builder.add_node("json", json_node)
builder.add_node("llm", llm_node)

builder.set_entry_point("csv")
builder.add_conditional_edges("csv", check_csv, {"json": "json", "llm": "llm"})
builder.add_conditional_edges("json", check_json, {"llm": "llm", "direct": END})
builder.add_edge("llm", END)

# Compile and run
app_graph = builder.compile()

# Run with input query
def run_pipeline(query: str, topic:str):
    initial_state = SearchState(query=query, topic=topic)
    final_state = app_graph.invoke(initial_state)
    return final_state["final_answer"]


response = run_pipeline("What is distal radius?", "Distal_radius")
print(response)