import os
import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

# ---- CONFIG ---- #
BASE_DIR = os.path.dirname(__file__)
INPUT_JSON_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "json_for_embeddings", "book_jsons"))
OUTPUT_BASE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "embeddings"))
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

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
                doc = Document(page_content=text, metadata={"topic": topic, "source": os.path.basename(json_file)})
                documents.append(doc)
        else:
            print(f"[⚠️] Skipped non-dict entry in {json_file}: {type(entry)}")
    return documents

def save_to_faiss(folder_name: str, documents: list[Document]):
    folder_safe_name = folder_name.replace(" ", "_")
    persist_dir = os.path.join(OUTPUT_BASE_DIR, folder_safe_name)
    os.makedirs(persist_dir, exist_ok=True)
    db = FAISS.from_documents(documents, EMBEDDING_MODEL)
    db.save_local(persist_dir)
    print(f"[✅] Saved FAISS index for '{folder_name}' to {persist_dir}")

# ---- MAIN ---- #
def process_all_folders():
    if not os.path.isdir(INPUT_JSON_DIR):
        print(f"[❌] Input directory not found: {INPUT_JSON_DIR}")
        return

    for root, dirs, files in os.walk(INPUT_JSON_DIR):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                parent_folder = os.path.basename(os.path.dirname(file_path))  # Get folder name where JSON is located
                print(f"\n📄 Processing: {file_path} (Folder: {parent_folder})")

                try:
                    docs = load_json_entries(file_path)
                    if docs:
                        save_to_faiss(parent_folder, docs)
                except Exception as e:
                    print(f"[⚠️] Failed to process {file_path}: {e}")

if __name__ == "__main__":
    process_all_folders()
