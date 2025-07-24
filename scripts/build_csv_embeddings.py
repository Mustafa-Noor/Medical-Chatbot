import os
import csv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

# ---- CONFIG ---- #
BASE_DIR = os.path.dirname(__file__)
INPUT_CSV_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "csvs"))
OUTPUT_BASE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "csv_embeddings"))
FAILED_ROWS_LOG = os.path.join(OUTPUT_BASE_DIR, "failed_rows.csv")
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ---- HELPERS ---- #
def safe_strip(val):
    return val.strip() if isinstance(val, str) else ""

def row_to_text_vector(row: dict) -> str:
    question = safe_strip(row.get("question"))
    answer = safe_strip(row.get("answer"))
    topic = safe_strip(row.get("topic"))
    subtopic = safe_strip(row.get("subtopic"))
    follow_ups = safe_strip(row.get("follow_up_questions"))
    follow_up_answers = safe_strip(row.get("follow_up_answers"))
    keywords = safe_strip(row.get("keywords"))

    if not question or not answer:
        return None

    parts = [
        f"Topic: {topic}" if topic else "",
        f"Subtopic: {subtopic}" if subtopic else "",
        f"Q: {question}",
        f"A: {answer}",
        f"Follow-ups: {follow_ups} -> {follow_up_answers}" if follow_ups and follow_up_answers else "",
        f"Keywords: {keywords}" if keywords else ""
    ]
    return "\n".join([p for p in parts if p])

def load_csv_entries(csv_path: str) -> tuple[list[Document], list[dict]]:
    documents = []
    failed = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # header is row 1
            try:
                question = safe_strip(row.get("question"))
                answer = safe_strip(row.get("answer"))
                if not question or not answer:
                    raise ValueError("Missing question or answer")

                text = row_to_text_vector(row)
                if not text:
                    raise ValueError("Generated text vector is empty")

                metadata = {
                    "topic": safe_strip(row.get("topic")),
                    "subtopic": safe_strip(row.get("subtopic")),
                    "source": os.path.basename(csv_path),
                    "question": question,
                    "answer": answer,
                    "keywords": safe_strip(row.get("keywords"))
                }

                documents.append(Document(page_content=text, metadata=metadata))

            except Exception as e:
                row["error_reason"] = str(e)
                row["source_file"] = os.path.basename(csv_path)
                row["source_folder"] = os.path.basename(os.path.dirname(csv_path))
                row["original_row_number"] = row_num
                failed.append(row)

    return documents, failed

def save_to_faiss(folder_name: str, documents: list[Document]):
    folder_safe_name = folder_name.replace(" ", "_")
    persist_dir = os.path.join(OUTPUT_BASE_DIR, folder_safe_name)
    os.makedirs(persist_dir, exist_ok=True)
    db = FAISS.from_documents(documents, EMBEDDING_MODEL)
    db.save_local(persist_dir)
    print(f"[✅] Saved FAISS index for '{folder_name}' to {persist_dir}")



# ---- MAIN ---- #
def process_all_csvs():
    all_failed = []
    for root, _, files in os.walk(INPUT_CSV_DIR):
        for file in files:
            if not file.endswith(".csv"):
                continue
            path = os.path.join(root, file)
            folder_name = os.path.basename(root)
            print(f"[📄] Processing {file} from {folder_name}")

            docs, failed = load_csv_entries(path)
            if docs:
                save_to_faiss(folder_name, docs)
            if failed:
                all_failed.extend(failed)


if __name__ == "__main__":
    process_all_csvs()
