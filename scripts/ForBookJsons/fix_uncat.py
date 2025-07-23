import json
from collections import Counter

# ---------- File Path ----------
topics_file = "topics.json"

# Load JSON
with open(topics_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Count topic names
topic_counter = Counter()

for major in data.get("major_topics", []):
    for topic in major.get("topics", []):
        topic_name = topic.get("topic", "").strip()
        if topic_name:
            topic_counter[topic_name] += 1

# Sort and print
print("📊 Topic Frequencies:\n")
for topic, count in topic_counter.most_common():
    print(f"{topic}: {count}")

# Total unique topics
print(f"\n🧮 Total unique topic names: {len(topic_counter)}")
print(f"📦 Total topic entries: {sum(topic_counter.values())}")
