from app.services.json_search import search_json
from app.schemas.search_state import SearchState

import logging
logger = logging.getLogger()

def json_node(state: SearchState) -> SearchState:
    print("DEBUG: Entered json_node")
    logger.info("json Starting")
    result = search_json(state.topic, state.query, state.query_vector)
    logger.info("json ending")
    print("DEBUG: JSON Result =", result)
    state.json_score = result["score"]
    state.json_docs = result["docs"]
    return state