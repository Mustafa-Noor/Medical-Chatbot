from langgraph.graph import StateGraph, END
from app.schemas.search_state import SearchState
from app.pipelines.nodes.csv_node import csv_node
from app.pipelines.nodes.json_node import json_node
from app.pipelines.nodes.llm_node import llm_with_context_node, llm_direct_node
from app.pipelines.conditions import check_csv_score, check_json_score
from app.pipelines.nodes.embed_node import embed_node

def build_graph():
    print("DEBUG: Building LangGraph pipeline...")
    builder = StateGraph(SearchState)

    builder.add_node("embed", embed_node)
    builder.add_node("csv", csv_node)
    builder.add_node("json", json_node)
    builder.add_node("llm_with_context", llm_with_context_node)
    builder.add_node("llm_direct", llm_direct_node)

    builder.set_entry_point("embed")

    builder.add_edge("embed", "csv")

    builder.add_conditional_edges("csv", check_csv_score, {
        "llm_with_context": "llm_with_context",
        "json": "json"
    })

    builder.add_conditional_edges("json", check_json_score, {
        "llm_with_context": "llm_with_context",
        "llm_direct": "llm_direct"
    })

    builder.add_edge("llm_with_context", END)
    builder.add_edge("llm_direct", END)

    print("DEBUG: Graph build complete.")
    return builder.compile()
