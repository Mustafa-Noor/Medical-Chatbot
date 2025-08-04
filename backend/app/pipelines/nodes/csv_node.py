from app.services.csv_search import search_csv
from app.schemas.search_state import SearchState

def csv_node(state: SearchState) -> SearchState:
    print("DEBUG: Entered csv_node")
    result = search_csv(state.topic, state.query)
    print("DEBUG: CSV Result =", result)
    state.csv_score = result["score"]
    state.csv_docs = result["docs"]
    return state