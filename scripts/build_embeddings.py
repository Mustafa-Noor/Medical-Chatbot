# import os
# import sys
# import asyncio
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_experimental.text_splitter import SemanticChunker
# from langchain_community.vectorstores import FAISS
# from langchain.schema import Document
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()


# # ---- CONFIG ---- #
# BASE_PDF_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pdfs", "Reference Material"))
# OUTPUT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "embeddings"))
# EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# # ---- HELPERS ---- #
# async def load_pdf(file_path: str, topic: str) -> list[Document]:
#     loader = PyPDFLoader(file_path)
#     documents = []
#     async for page in loader.alazy_load():
#         page.metadata["topic"] = topic
#         page.metadata["source"] = os.path.basename(file_path)
#         documents.append(page)
#     return documents

# def semantic_split(documents: list[Document]) -> list[Document]:
#     chunker = SemanticChunker(EMBEDDING_MODEL)
#     return chunker.split_documents(documents)

# def save_to_faiss(topic: str, chunks: list[Document]):
#     persist_dir = os.path.join(OUTPUT_BASE_DIR, topic.lower().replace(" ", "_"))
#     os.makedirs(persist_dir, exist_ok=True)
#     db = FAISS.from_documents(chunks, EMBEDDING_MODEL)
#     db.save_local(persist_dir)
#     print(f"[✅] Saved FAISS index for {topic} to: {persist_dir}")

# # ---- MAIN PROCESSOR (one folder at a time) ---- #
# async def process_single_topic(topic_name: str):
#     topic_folder = os.path.join(BASE_PDF_DIR, topic_name)

#     if not os.path.isdir(topic_folder):
#         print(f"[❌] Folder '{topic_name}' does not exist in Reference Material.")
#         return

#     all_chunks = []
#     pdf_files = [f for f in os.listdir(topic_folder) if f.lower().endswith(".pdf")]

#     if not pdf_files:
#         print(f"[⚠️] No PDFs found in {topic_name}.")
#         return

#     for file in pdf_files:
#         file_path = os.path.join(topic_folder, file)
#         print(f"[🔍] Processing {file} in {topic_name}...")

#         try:
#             docs = await load_pdf(file_path, topic_name)
#             chunks = semantic_split(docs)
#             all_chunks.extend(chunks)
#         except Exception as e:
#             print(f"[⚠️] Failed to process {file_path}: {e}")

#     if all_chunks:
#         save_to_faiss(topic_name.lower().replace(" ", "_"), all_chunks)
#     else:
#         print(f"[⚠️] No valid chunks created from {topic_name}.")

# # ---- MAIN: Process all topics ---- #
# async def process_all_topics():
#     topic_dirs = [d for d in os.listdir(BASE_PDF_DIR) if os.path.isdir(os.path.join(BASE_PDF_DIR, d))]

#     if not topic_dirs:
#         print("[❌] No folders found in 'Reference Material'.")
#         return

#     for topic in topic_dirs:
#         print(f"\n📁 Starting processing for topic: {topic}")
#         await process_single_topic(topic)

# if __name__ == "__main__":
#     asyncio.run(process_all_topics())


# import os
# import json
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain.schema import Document

# # ---- CONFIG ---- #
# BASE_DIR = os.path.dirname(__file__)
# #INPUT_JSON_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "structured_json_books", "book_jsons"))
# INPUT_JSON_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "structured_json"))
# OUTPUT_BASE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "embeddings"))
# EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# # ---- HELPERS ---- #
# def load_json_entries(json_file: str) -> list[Document]:
#     with open(json_file, "r", encoding="utf-8") as f:
#         entries = json.load(f)

#     documents = []
#     for entry in entries:
#         if isinstance(entry, dict):
#             topic = entry.get("topic", "").strip()
#             text = entry.get("text", "").strip()
#             if topic and text:
#                 doc = Document(page_content=text, metadata={"topic": topic, "source": os.path.basename(json_file)})
#                 documents.append(doc)
#         else:
#             print(f"[⚠️] Skipped non-dict entry in {json_file}: {type(entry)}")
#     return documents

# def save_to_faiss(folder_name: str, documents: list[Document]):
#     folder_safe_name = folder_name.replace(" ", "_")
#     persist_dir = os.path.join(OUTPUT_BASE_DIR, folder_safe_name)
#     os.makedirs(persist_dir, exist_ok=True)
#     db = FAISS.from_documents(documents, EMBEDDING_MODEL)
#     db.save_local(persist_dir)
#     print(f"[✅] Saved FAISS index for '{folder_name}' to {persist_dir}")

# # ---- MAIN ---- #
# def process_all_folders():
#     if not os.path.isdir(INPUT_JSON_DIR):
#         print(f"[❌] Input directory not found: {INPUT_JSON_DIR}")
#         return

#     for root, dirs, files in os.walk(INPUT_JSON_DIR):
#         for file in files:
#             if file.endswith(".json"):
#                 file_path = os.path.join(root, file)
#                 parent_folder = os.path.basename(os.path.dirname(file_path))  # Get folder name where JSON is located
#                 print(f"\n📄 Processing: {file_path} (Folder: {parent_folder})")

#                 try:
#                     docs = load_json_entries(file_path)
#                     if docs:
#                         save_to_faiss(parent_folder, docs)
#                 except Exception as e:
#                     print(f"[⚠️] Failed to process {file_path}: {e}")

# if __name__ == "__main__":
#     process_all_folders()


import os
import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from more_itertools import chunked  # ✅ for batching

# ---- CONFIG ---- #
BASE_DIR = os.path.dirname(__file__)
INPUT_JSON_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "structured_json_books", "book_jsons"))
#INPUT_JSON_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "structured_json"))
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# ✅ Qdrant Cloud Configuration
QDRANT_URL = "https://33acd362-b59a-41a7-819c-98238df488d1.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.c-7a3RnZ-gujNMLWO0iz7W5DR2u4RDlt4oHUL1dn2IM"
VECTOR_SIZE = 384  # Must match embedding dimension

# ---- INIT QDRANT CLIENT ---- #
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=30.0  # ✅ Increased timeout
)

# ---- HELPERS ---- #
def load_json_entries(json_file: str) -> list[Document]:
    with open(json_file, "r", encoding="utf-8") as f:
        entries = json.load(f)

    documents = []
    for entry in entries:
        if isinstance(entry, dict):
            topic = entry.get("topic", "").strip()
            text = entry.get("text", "").strip()
            if topic and text:
                doc = Document(
                    page_content=text,
                    metadata={"topic": topic, "source": os.path.basename(json_file)}
                )
                documents.append(doc)
        else:
            print(f"[⚠️] Skipped non-dict entry in {json_file}: {type(entry)}")
    return documents

def save_to_qdrant(collection_name: str, documents: list[Document]):
    # Ensure collection exists
    try:
        qdrant_client.get_collection(collection_name)
    except Exception:
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

    batch_size = 10
    total_uploaded = 0

    for i, batch in enumerate(chunked(documents, batch_size)):
        try:
            _ = Qdrant.from_documents(
                documents=batch,
                embedding=EMBEDDING_MODEL,
                collection_name=collection_name,
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY,
            )
            total_uploaded += len(batch)
            print(f"[✅] Uploaded batch {i+1} ({len(batch)} docs)")
        except Exception as e:
            print(f"[❌] Batch {i+1} failed: {e}")

    print(f"[🎉] Uploaded total {total_uploaded} documents to collection '{collection_name}'")

# ---- MAIN ---- #
def process_all_folders():
    if not os.path.isdir(INPUT_JSON_DIR):
        print(f"[❌] Input directory not found: {INPUT_JSON_DIR}")
        return

    for root, dirs, files in os.walk(INPUT_JSON_DIR):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                parent_folder = os.path.basename(os.path.dirname(file_path))  # Folder = collection name
                print(f"\n📄 Processing: {file_path} (Collection: {parent_folder})")

                try:
                    docs = load_json_entries(file_path)
                    if docs:
                        save_to_qdrant(parent_folder, docs)
                except Exception as e:
                    print(f"[⚠️] Failed to process {file_path}: {e}")

if __name__ == "__main__":
    process_all_folders()


