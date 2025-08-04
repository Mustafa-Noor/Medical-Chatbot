from app.services.json_search import search_json
from app.schemas.search_state import SearchState

def json_node(state: SearchState) -> SearchState:
    print("DEBUG: Entered json_node")
    result = search_json(state.topic, state.query)
    print("DEBUG: JSON Result =", result)
    state.json_score = result["score"]
    state.json_docs = result["docs"]
    return state