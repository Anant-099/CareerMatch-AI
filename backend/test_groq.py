
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing from backend/.env"
    )

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": "Reply exactly: Groq connection successful."
            }
        ],
    )

    print(response.choices[0].message.content)

except Exception as exc:
    print("Groq API test failed.")
    print("Error type:", type(exc).__name__)
    print("Error details:", str(exc))
