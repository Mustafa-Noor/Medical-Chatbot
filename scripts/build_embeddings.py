import os
import sys
import asyncio
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ---- CONFIG ---- #
BASE_PDF_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pdfs", "Reference Material"))
OUTPUT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "embeddings"))
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ---- HELPERS ---- #
async def load_pdf(file_path: str, topic: str) -> list[Document]:
    loader = PyPDFLoader(file_path)
    documents = []
    async for page in loader.alazy_load():
        page.metadata["topic"] = topic
        page.metadata["source"] = os.path.basename(file_path)
        documents.append(page)
    return documents

def semantic_split(documents: list[Document]) -> list[Document]:
    chunker = SemanticChunker(EMBEDDING_MODEL)
    return chunker.split_documents(documents)

def save_to_faiss(topic: str, chunks: list[Document]):
    persist_dir = os.path.join(OUTPUT_BASE_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(persist_dir, exist_ok=True)
    db = FAISS.from_documents(chunks, EMBEDDING_MODEL)
    db.save_local(persist_dir)
    print(f"[✅] Saved FAISS index for {topic} to: {persist_dir}")

# ---- MAIN PROCESSOR (one folder at a time) ---- #
async def process_single_topic(topic_name: str):
    topic_folder = os.path.join(BASE_PDF_DIR, topic_name)

    if not os.path.isdir(topic_folder):
        print(f"[❌] Folder '{topic_name}' does not exist in Reference Material.")
        return

    all_chunks = []
    pdf_files = [f for f in os.listdir(topic_folder) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"[⚠️] No PDFs found in {topic_name}.")
        return

    for file in pdf_files:
        file_path = os.path.join(topic_folder, file)
        print(f"[🔍] Processing {file} in {topic_name}...")

        try:
            docs = await load_pdf(file_path, topic_name)
            chunks = semantic_split(docs)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"[⚠️] Failed to process {file_path}: {e}")

    if all_chunks:
        save_to_faiss(topic_name.lower().replace(" ", "_"), all_chunks)
    else:
        print(f"[⚠️] No valid chunks created from {topic_name}.")

# ---- MAIN: Process all topics ---- #
async def process_all_topics():
    topic_dirs = [d for d in os.listdir(BASE_PDF_DIR) if os.path.isdir(os.path.join(BASE_PDF_DIR, d))]

    if not topic_dirs:
        print("[❌] No folders found in 'Reference Material'.")
        return

    for topic in topic_dirs:
        print(f"\n📁 Starting processing for topic: {topic}")
        await process_single_topic(topic)

if __name__ == "__main__":
    asyncio.run(process_all_topics())
