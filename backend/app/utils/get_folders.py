import os
from app.config import settings

def get_topic_folders(embeddings_dir: str = settings.CSV_EMBEDDINGS_DIR) -> list[dict]:
    """
    Reads folders from the embeddings directory and returns them
    as a list of {value, label} dicts, sorted alphabetically.
    """
    try:
        topics = [
            {
                "value": folder,
                "label": folder.replace("__", ": ").replace("_", " ")
            }
            for folder in os.listdir(embeddings_dir)
            if os.path.isdir(os.path.join(embeddings_dir, folder))
        ]
        topics.sort(key=lambda x: x["label"])
        return topics
    except Exception as e:
        raise RuntimeError(f"Failed to read topic folders: {e}")
