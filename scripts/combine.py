import os
import json

# Base folder where structured_json is located
BASE_DIR = os.path.dirname(__file__)
INPUT_JSON_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "structured_json"))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "structured_json_books", "pdf_jsons"))

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Go through each subfolder in structured_json
for folder_name in os.listdir(INPUT_JSON_DIR):
    folder_path = os.path.join(INPUT_JSON_DIR, folder_name)
    
    if os.path.isdir(folder_path):
        combined_data = []
        print(f"🔄 Processing folder: {folder_name}")

        for file_name in os.listdir(folder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(folder_path, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            combined_data.extend(data)
                        else:
                            combined_data.append(data)
                except Exception as e:
                    print(f"⚠️ Error in file {file_name}: {e}")

        # Save the combined JSON for this folder
        output_file = os.path.join(OUTPUT_DIR, f"{folder_name}.json")
        with open(output_file, "w", encoding="utf-8") as out_f:
            json.dump(combined_data, out_f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(combined_data)} items to {output_file}")
