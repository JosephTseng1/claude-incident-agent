import os

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def ask_claude(service: str, description: str):
    message = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Investigate this service incident.\n"
                    f"Service: {service}\n"
                    f"Description: {description}"
                )
            }
        ]
    )

    for block in message.content:
        if block.type == "text":
            return block.text

    raise RuntimeError("Claude returned no text response.")