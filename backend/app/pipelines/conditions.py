def check_csv_score(state):
    print(f"DEBUG: CSV Score = {state.csv_score}")
    
    if not state.csv_docs:
        print("DEBUG: No CSV docs — routing to JSON")
        return "json"

    print("DEBUG: Exact match in CSV — routing to llm_with_context")
    return "llm_with_context"


def check_json_score(state):
    print(f"DEBUG: JSON Score = {state.json_score}")

    if not state.json_docs:
        print("DEBUG: No JSON docs — routing to llm_direct")
        return "llm_direct"

    print("DEBUG: Found JSON docs — routing to llm_with_context")
    return "llm_with_context"
