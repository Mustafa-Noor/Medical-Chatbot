import json

def merge_topic_with_text(topics_json, new_entry):
    topic_name = new_entry["topic"]
    new_text = new_entry["text"]

    for major in topics_json["major_topics"]:
        for topic in major["topics"]:
            if topic["topic"] == topic_name:
                if "text" in topic and topic["text"] == new_text:
                    print(f"🔁 Exact topic-text already exists under '{major['major_topic']}'. Skipping.")
                    return topics_json
                elif "text" not in topic:
                    topic["text"] = new_text
                    print(f"📝 Added text to existing topic under '{major['major_topic']}'.")
                    return topics_json
                else:
                    major["topics"].append({
                        "topic": topic_name,
                        "text": new_text
                    })
                    print(f"➕ Added duplicate topic with new text under '{major['major_topic']}'.")
                    return topics_json

    # Topic not found — add to "Uncategorized"
    print(f"⚠️ Topic '{topic_name}' not found. Adding under 'Uncategorized'")
    for major in topics_json["major_topics"]:
        if major["major_topic"] == "Uncategorized":
            major["topics"].append({
                "topic": topic_name,
                "text": new_text
            })
            return topics_json

    # If "Uncategorized" doesn't exist, create it
    topics_json["major_topics"].append({
        "major_topic": "Uncategorized",
        "topics": [{
            "topic": topic_name,
            "text": new_text
        }]
    })

    return topics_json

# ----------- File paths -----------
topics_file = "topics.json"
new_topic_file = "frcs.json"

# ----------- Load files -----------
with open(topics_file, "r") as f:
    topics_json = json.load(f)

with open(new_topic_file, "r") as f:
    new_data = json.load(f)

# ----------- Handle list or single entry -----------
if isinstance(new_data, list):
    for entry in new_data:
        topics_json = merge_topic_with_text(topics_json, entry)
else:
    topics_json = merge_topic_with_text(topics_json, new_data)

# ----------- Save updated JSON -----------
with open(topics_file, "w") as f:
    json.dump(topics_json, f, indent=2)

print("✅ Merge completed.")
