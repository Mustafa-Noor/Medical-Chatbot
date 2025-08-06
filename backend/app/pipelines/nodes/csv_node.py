from app.services.csv_search import search_csv
from app.schemas.search_state import SearchState
import logging
logger = logging.getLogger()

def csv_node(state: SearchState) -> SearchState:
    print("DEBUG: Entered csv_node")
    logger.info("CSv Starting")
    result = search_csv(state.topic, state.query, state.query_vector)
    print("DEBUG: CSV Result =", result)
    logger.info("CSV DONe")
    state.csv_score = result["score"]
    state.csv_docs = result["docs"]
    return state