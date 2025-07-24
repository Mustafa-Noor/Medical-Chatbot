import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure API key from environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Choose the right model (text-only: gemini-pro)
model = genai.GenerativeModel("gemini-2.5-flash")

# Generate response
response = model.generate_content("Explain how AI works in a few words")

# Print response
print(response.text)
