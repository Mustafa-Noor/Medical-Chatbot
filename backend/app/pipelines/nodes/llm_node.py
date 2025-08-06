from app.services.llm_context import generate_response
from app.schemas.search_state import SearchState
import logging
logger = logging.getLogger()

def llm_with_context_node(state: SearchState) -> SearchState:
    print("DEBUG: Entered llm_with_context_node")

    memory_context = state.memory or ""
    knowledge_context = ""

    if state.csv_docs:
        print("DEBUG: Using CSV docs for knowledge context")
        knowledge_context = "\n\n".join([doc.page_content for doc in state.csv_docs])
        state.source = "csv"

    elif state.json_docs:
        print("DEBUG: Using JSON docs for knowledge context")
        knowledge_context = "\n\n".join([doc.page_content for doc in state.json_docs])
        state.source = "rag"

    else:
        print("DEBUG: No docs found — fallback to LLM")
        state.source = "llm"

    print("DEBUG: Knowledge Context Length =", len(knowledge_context))
    print("DEBUG: Memory Context Length =", len(memory_context))

    logger.info("generating start=-------")
    state.final_answer = generate_response(state.query, knowledge_context, memory_context, state.topic)
    logger.info("generating end=-------")
    print("DEBUG: Final Answer =", state.final_answer[:100])
    return state


def llm_direct_node(state: SearchState) -> SearchState:
    print("DEBUG: Entered llm_direct_node")
    state.final_answer = generate_response(state.query, "", state.memory, state.topic)
    print("DEBUG: Final Answer (Direct LLM) =", state.final_answer[:100])
    state.source = "llm"
    return state
