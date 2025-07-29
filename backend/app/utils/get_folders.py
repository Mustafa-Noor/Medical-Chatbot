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


# def get_topic_folders() -> list[dict]:
#     """
#     Fetch collections from Qdrant that end with '_csv',
#     and return them as a list of {value, label} dicts.
#     """
#     try:
#         collections_info = client.get_collections()
#         all_collections = [c.name for c in collections_info.collections]

#         topics = [
#             {
#                 "value": name,
#                 "label": name.removesuffix("_csv").replace("__", ": ").replace("_", " ")
#             }
#             for name in all_collections if name.lower().endswith("_csv")
#         ]

#         topics.sort(key=lambda x: x["label"])
#         return topics

#     except Exception as e:
#         raise RuntimeError(f"Failed to fetch collections: {e}")



        
