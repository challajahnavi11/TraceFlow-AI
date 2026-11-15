
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Locate the project root and load the .env file.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Check your project's .env file."
    )

# Initialize the Groq client.
client = Groq(api_key=api_key)

print("Connecting to Groq...")

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": "Introduce yourself in one short sentence."
            }
        ],
        temperature=0.3,
        max_completion_tokens=100
    )

    print("\nGroq connection successful!")
    print("LLM Response:")
    print(response.choices[0].message.content)

except Exception as error:
    print("\nGroq connection failed.")
    print("Error:", str(error))
