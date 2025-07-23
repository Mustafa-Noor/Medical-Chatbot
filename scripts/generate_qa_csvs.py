import os
import json
import csv
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# ---- SETUP ---- #
BASE_DIR = os.path.dirname(__file__)
INPUT_JSON_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "structured_json"))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "csvs"))

# Load .env and Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini model
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# Prompt builder
def build_prompt(topic, subtopic, text):
    return f"""
I have structured JSON files containing medical content. Each JSON has fields like heading, topic, subtopic, and text. I want to convert these into CSV rows that are optimized for semantic search and downstream NLP tasks like question answering, retrieval, and chatbot systems.

Please generate a CSV where each row represents a high-quality QnA pair extracted or inferred from the text. The CSV should have the following columns:

topic – The main subject discussed (from topic)
subtopic – A more specific area within the topic (from subtopic)
question – A natural-language question that a user might ask based on the text
answer – A concise, accurate answer based on the text
follow_up_questions – (Optional) Related or follow-up questions (comma-separated)
follow_up_answers – Answers corresponding to follow-up questions (same order)
keywords – Important medical terms or phrases from the content that help in semantic filtering (comma-separated)

Notes:
- The text might be a paragraph, but break it down into multiple QnA pairs if needed.
- Ensure each question is distinct and answerable by the given text.
- Keep answers factual, specific, and medically accurate.
- Use follow-up questions only when meaningful (don’t force them).

Now here is the content:
Topic: {topic}
Subtopic: {subtopic}
Text: {text}
Please provide the output in CSV format (only the data rows, no column names).
"""

# Process a single folder
def process_folder(folder_path, output_csv_path):
    csv_rows = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    entries = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse {filename}: {e}")
                    continue

            if not isinstance(entries, list):
                print(f"⚠️ Skipping {filename} (not a list of entries)")
                continue

            for entry in entries:
                topic = entry.get("topic", "")
                subtopic = entry.get("subtopic", "")
                text = entry.get("text", "")

                if not text.strip():
                    continue  # Skip empty texts

                prompt = build_prompt(topic, subtopic, text)
                try:
                    response = model.generate_content(prompt)
                    csv_text = response.text.strip()

                    for line in csv_text.split("\n"):
                        if line.strip():
                            parts = [part.strip().strip('"') for part in line.split(",")]
                            while len(parts) < 7:
                                parts.append("")
                            csv_rows.append(parts)
                except Exception as e:
                    print(f"❌ Error generating from {filename}: {e}")

    # Save CSV
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "topic",
            "subtopic",
            "question",
            "answer",
            "follow_up_questions",
            "follow_up_answers",
            "keywords"
        ])
        writer.writerows(csv_rows)
    print(f"✅ CSV created: {output_csv_path}")


# ---- MAIN ---- #
def main():
    if len(sys.argv) < 2:
        print("❌ Please provide a folder name as an argument.")
        print("Usage: python script.py <folder_name>")
        return

    folder_name = sys.argv[1]
    folder_path = os.path.join(INPUT_JSON_DIR, folder_name)

    if not os.path.isdir(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return

    output_csv_path = os.path.join(OUTPUT_DIR, folder_name, "output.csv")
    print(f"📂 Processing folder: {folder_name}")
    process_folder(folder_path, output_csv_path)

if __name__ == "__main__":
    main()
