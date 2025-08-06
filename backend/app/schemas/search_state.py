from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from langchain_core.documents import Document 
from typing import Optional
import numpy as np # or your own Document class

class SearchState(BaseModel):
    query: str
    csv_score: Optional[float] = None
    csv_docs: Optional[List[Document]] = None
    json_score: Optional[float] = None
    json_docs: Optional[List[Document]] = None
    final_answer: Optional[str] = None
    topic: str  # <-- Add this
    source: Optional[str] = "llm"
    memory: Optional[str] = ""
    query_vector: Optional[np.ndarray] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
