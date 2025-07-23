#!/usr/bin/env python3
"""
Script to convert hierarchical medical topic text into structured JSON format.
Converts from text format with headers and bullet points to JSON with major_topics and topics.
"""

import json
import re
from typing import Dict, List, Any

def parse_medical_topics_text(text: str) -> Dict[str, Any]:
    """
    Parse the medical topics text and convert to structured JSON format.
    
    Args:
        text (str): Input text with hierarchical structure
        
    Returns:
        Dict[str, Any]: Structured data with major_topics containing topics
    """
    lines = text.strip().split('\n')
    result = {"major_topics": []}
    
    current_major_topic = None
    current_subtopic = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if it's a major heading (### **Title**)
        major_heading_match = re.match(r'^### \*\*(.*?)\*\*$', line)
        if major_heading_match:
            major_topic_name = major_heading_match.group(1)
            current_major_topic = {
                "major_topic": major_topic_name,
                "topics": []
            }
            result["major_topics"].append(current_major_topic)
            current_subtopic = None
            continue
            
        # Check if it's a subtopic heading (*   **Title**)
        subtopic_match = re.match(r'^\*\s+\*\*(.*?)\*\*$', line)
        if subtopic_match:
            subtopic_name = subtopic_match.group(1)
            current_subtopic = {
                "topic": subtopic_name,
                "text": []
            }
            if current_major_topic:
                current_major_topic["topics"].append(current_subtopic)
            continue
            
        # Check if it's a nested subtopic (*   **Title**) - for deeper nesting
        nested_subtopic_match = re.match(r'^\s+\*\s+\*\*(.*?)\*\*$', line)
        if nested_subtopic_match:
            nested_subtopic_name = nested_subtopic_match.group(1)
            nested_subtopic = {
                "topic": nested_subtopic_name,
                "text": []
            }
            if current_subtopic:
                # If we're already in a subtopic, add this as a nested topic
                if "subtopics" not in current_subtopic:
                    current_subtopic["subtopics"] = []
                current_subtopic["subtopics"].append(nested_subtopic)
            elif current_major_topic:
                current_major_topic["topics"].append(nested_subtopic)
            continue
            
        # Check if it's a regular topic item (starts with * and text)
        topic_item_match = re.match(r'^\s*\*\s+(.+)$', line)
        if topic_item_match:
            topic_text = topic_item_match.group(1).strip()
            
            # If we don't have a current subtopic, create one under current major topic
            if not current_subtopic and current_major_topic:
                current_subtopic = {
                    "topic": "General",
                    "text": []
                }
                current_major_topic["topics"].append(current_subtopic)
            
            if current_subtopic:
                current_subtopic["text"].append(topic_text)
    
    return result

def convert_to_flat_format(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert structured data into a flat format where each text entry becomes its own topic.
    
    Returns:
        Dict[str, Any]: Flattened format
    """
    flat_format = {"major_topics": []}

    for major_topic_data in structured_data["major_topics"]:
        major_topic_entry = {
            "major_topic": major_topic_data["major_topic"],
            "topics": []
        }

        for topic_data in major_topic_data["topics"]:
            # Convert each text item to its own topic
            for item in topic_data.get("text", []):
                major_topic_entry["topics"].append({
                    "topic": item
                })

            # Handle subtopics if present
            for sub in topic_data.get("subtopics", []):
                for subitem in sub.get("text", []):
                    major_topic_entry["topics"].append({
                        "topic": subitem
                    })

        flat_format["major_topics"].append(major_topic_entry)

    return flat_format


def main():
    """Main function to run the conversion"""
    # Example usage
    input_file = "merged_topics.txt"  # Change this to your input file
    output_file = "medical_topics.json"  # Output JSON file
    
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            text_content = file.read()
        
        # Parse the text
        print("Parsing medical topics text...")
        structured_data = parse_medical_topics_text(text_content)
        
        # Convert to simple format
        print("Converting to requested format...")
        simple_data = convert_to_simple_format(structured_data)
        
        # Write to JSON file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(simple_data, file, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted to JSON format!")
        print(f"Output saved to: {output_file}")
        print(f"Number of major topics: {len(simple_data['major_topics'])}")
        
        # Print summary
        for major_topic in simple_data['major_topics']:
            print(f"- {major_topic['major_topic']}: {len(major_topic['topics'])} topics")
    
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        print("Please make sure the file exists or update the file path in the script.")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

# Alternative function to process text directly (for testing)
def process_text_directly(text: str) -> str:
    """
    Process text directly and return JSON string
    
    Args:
        text (str): Input text
        
    Returns:
        str: JSON formatted string
    """
    structured_data = parse_medical_topics_text(text)
    simple_data = convert_to_flat_format(structured_data)
    return json.dumps(simple_data, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert structured topic text into flat JSON.")
    parser.add_argument("--input", type=str, required=True, help="Path to input .txt file")
    parser.add_argument("--output", type=str, default="topics.json", help="Output JSON filename")

    args = parser.parse_args()

    # Read input text file
    with open(args.input, "r", encoding="utf-8") as f:
        input_text = f.read()

    # Parse and convert
    structured_data = parse_medical_topics_text(input_text)
    flat_data = convert_to_flat_format(structured_data)

    # Write to output file
    with open(args.output, "w", encoding="utf-8") as out_f:
        json.dump(flat_data, out_f, indent=2, ensure_ascii=False)

    print(f"Saved {args.output} with {len(flat_data['major_topics'])} major topics.")
