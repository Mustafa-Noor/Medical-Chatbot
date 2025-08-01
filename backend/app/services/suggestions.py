import os
import sys
from qdrant_client import QdrantClient
from typing import List
from fastapi import HTTPException
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.config import settings  # Make sure this exists

qdrant_client = QdrantClient(
    url=settings.Qdrant_url,
    api_key=settings.Qdrant_key,
)

def get_csv_suggestions(topic: str, count: int = 3) -> List[str]:
    topic = topic.strip() + "_csv"

    try:
        points = qdrant_client.scroll(
            collection_name=topic,
            with_vectors=False,
            with_payload=True,
            limit=500
        )[0]

        valid_points = [p.payload["question"] for p in points if p.payload and "question" in p.payload]

        if not valid_points:
            raise HTTPException(status_code=404, detail="No valid questions found.")

        return random.sample(valid_points, min(count, len(valid_points)))

    except Exception as e:
        print(f"❌ Error in get_csv_suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

