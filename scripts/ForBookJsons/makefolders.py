import json
import os

# -------- File Path --------
input_file = "Final.json"
output_base_dir = "book_jsons"  # Folder where all folders will go

# Create base directory if it doesn't exist
os.makedirs(output_base_dir, exist_ok=True)

# Load the main JSON
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Process each major topic
for major in data.get("major_topics", []):
    major_topic_name = major.get("major_topic", "").strip()

    if not major_topic_name:
        continue

    # Sanitize folder name (remove invalid characters)
    folder_name = "".join(c for c in major_topic_name if c.isalnum() or c in " _-").strip().replace(" ", "_")
    folder_path = os.path.join(output_base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Create JSON file for this major topic
    output_data = {
        "major_topic": major_topic_name,
        "topics": major.get("topics", [])
    }

    output_file_path = os.path.join(folder_path, f"{folder_name}.json")

    with open(output_file_path, "w", encoding="utf-8") as out_f:
        json.dump(output_data, out_f, indent=2, ensure_ascii=False)

    print(f"✅ Saved: {output_file_path}")

print("\n📁 All major topics exported into separate folders.")
