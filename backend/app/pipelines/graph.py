from langgraph.graph import StateGraph, END
# from app.services.csv_search import search_csv
# from app.services.json_search import search_json
# from app.services.llm_context import generate_response
# from app.schemas.search_state import SearchState

from ..services.csv_search import search_csv
from ..services.json_search import search_json
from ..services.llm_context import generate_response
from ..schemas.search_state import SearchState


def csv_node(state: SearchState) -> SearchState:
    """Search CSV data source"""
    result = search_csv(state.topic, state.query)
    state.csv_score = result["score"]
    state.csv_docs = result["docs"]
    return state


def json_node(state: SearchState) -> SearchState:
    """Search JSON data source"""
    result = search_json(state.topic, state.query)
    state.json_score = result["score"]
    state.json_docs = result["docs"]
    return state


# def llm_with_context_node(state: SearchState) -> SearchState:
#     """Generate LLM response using retrieved context"""
#     # Use CSV context if available, otherwise JSON context
#     if state.csv_docs:
#         context_docs = state.csv_docs
#         context = "\n\n".join([doc.page_content for doc in context_docs])
#     elif state.json_docs:
#         context_docs = state.json_docs
#         context = "\n\n".join([doc.page_content for doc in context_docs])
#     else:
#         context = ""
    
#     answer = generate_response(state.query, context)
#     state.final_answer = answer
#     return state

def llm_with_context_node(state: SearchState) -> SearchState:
    print("DEBUG: Entered llm_with_context_node")

    if state.csv_docs:
        print("DEBUG: Using CSV docs for context")
        context = "\n\n".join([doc.page_content for doc in state.csv_docs])
        state.source = "csv"
    elif state.json_docs:
        print("DEBUG: Using JSON docs for context")
        context = "\n\n".join([doc.page_content for doc in state.json_docs])
        state.source = "rag"
    else:
        print("DEBUG: No docs found — falling back to LLM")
        context = ""
        state.source = "llm"

    state.final_answer = generate_response(state.query, context)
    return state




# def llm_direct_node(state: SearchState) -> SearchState:
#     """Generate LLM response directly without context"""
#     # Pass query directly to LLM without any retrieved context
#     answer = generate_response(state.query, "")
#     state.final_answer = answer
#     return state

def llm_direct_node(state: SearchState) -> SearchState:
    answer = generate_response(state.query, "")
    state.final_answer = answer
    state.source = "llm"
    return state



# def check_csv_score(state: SearchState) -> str:
#     """Route based on CSV score"""
#     if state.csv_score < 0.5:
#         # CSV score is low, use CSV results with LLM
#         return "llm_with_context"
#     else:
#         # CSV score is high, try JSON search
#         return "json"


# def check_json_score(state: SearchState) -> str:
#     """Route based on JSON score"""
#     if state.json_score < 0.8:
#         # JSON score is low, use JSON results with LLM
#         return "llm_with_context"
#     else:
#         # JSON score is high, go directly to LLM without context
#         return "llm_direct"

# def check_csv_score(state: SearchState) -> str:
#     print(f"DEBUG: CSV Score = {state.csv_score}")
#     return "llm_with_context" if state.csv_score < 0.5 else "json"

def check_csv_score(state: SearchState) -> str:
    print(f"DEBUG: CSV Score = {state.csv_score}")
    
    # 👇 New logic: If no docs from CSV, go to JSON
    if not state.csv_docs:
        print("DEBUG: No CSV docs — routing to JSON")
        return "json"
    
    print("DEBUG: Exact match in CSV — routing to llm_with_context")
    return "llm_with_context"

def check_json_score(state: SearchState) -> str:
    print(f"DEBUG: JSON Score = {state.json_score}")

    if not state.json_docs:
        print("DEBUG: No JSON docs — routing to llm_direct")
        return "llm_direct"

    print("DEBUG: Found JSON docs — routing to llm_with_context")
    return "llm_with_context"



# Build the graph
builder = StateGraph(SearchState)

# Add nodes
builder.add_node("csv", csv_node)
builder.add_node("json", json_node)
builder.add_node("llm_with_context", llm_with_context_node)
builder.add_node("llm_direct", llm_direct_node)

# Set entry point
builder.set_entry_point("csv")

# Add conditional edges
builder.add_conditional_edges(
    "csv", 
    check_csv_score, 
    {"llm_with_context": "llm_with_context", "json": "json"}
)

builder.add_conditional_edges(
    "json", 
    check_json_score, 
    {"llm_with_context": "llm_with_context", "llm_direct": "llm_direct"}
)

# Add terminal edges
builder.add_edge("llm_with_context", END)
builder.add_edge("llm_direct", END)

# Compile the graph
app_graph = builder.compile()


def run_pipeline(query: str, topic: str) -> str:
    initial_state = SearchState(query=query, topic=topic)
    final_state = app_graph.invoke(initial_state)

    # Ensure it's a SearchState, not dict
    if isinstance(final_state, dict):
        final_state = SearchState(**final_state)

    print("DEBUG: Final Source =", final_state.source)  # ✅ Add this
    print("DEBUG: Final Answer =", final_state.final_answer[:80])


    # return final_state.final_answer or "No answer generated."
    return {
        "answer": final_state.final_answer or "No answer generated.",
        "source": final_state.source or "llm"
    }


if __name__ == "__main__":
    print("\n[🧠 LangGraph Decision Flow]")
    print(app_graph.get_graph().print_ascii())

# # Example usage
# if __name__ == "__main__":
#     response = run_pipeline("What is distal radius?", "Distal_radius")
#     print(response)