import google.generativeai as genai
from app.config import settings

# Configure Gemini API once
genai.configure(api_key=settings.Google_key)

# Load the model once at module level
model = genai.GenerativeModel("gemini-2.5-flash")


def call_llm(prompt: str) -> str:
    """
    Generates a response using Gemini LLM given a user prompt.
    
    Args:
        prompt (str): The question or instruction for the LLM.
    
    Returns:
        str: The LLM-generated response text.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"
