from app.services.json_search import search_json
from app.schemas.search_state import SearchState
from typing import List
import numpy as np
import logging
import google.generativeai as genai
import sys
import os
logger = logging.getLogger()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.config import settings

# ---- CONFIG ---- #
genai.configure(api_key=settings.Google_key)
EMBEDDING_MODEL = "models/embedding-001"


def embed_with_gemini(text: str) -> List[float]:
    """Generate Gemini embeddings for a query."""
    response = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_query"
    )
    return response["embedding"]

def embed_node(state: SearchState) -> SearchState:
    logger.info("DEBUG: Embedding query...")
    embedding = np.array(embed_with_gemini(state.query)).reshape(1, -1)
    state.query_vector = embedding
    logger.info("DEBUG: Embedding query... made")
    return state