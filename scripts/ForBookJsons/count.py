import json
from collections import Counter

# 🔄 Load JSON file
with open("miller.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# 📊 Count topics
topic_counts = Counter(entry["topic"] for entry in data)

# 📋 Print sorted topic counts
print("\nTopic Frequencies:\n")
for topic, count in topic_counts.most_common():
    print(f"{topic}: {count}")