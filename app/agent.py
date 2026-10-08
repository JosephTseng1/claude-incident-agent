import os

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

TOOLS = [
    {
        "name": "search_logs",
        "description": "Search service logs for messages containing a keyword.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Name of the service to search."
                },
                "keyword": {
                    "type": "string",
                    "description": "Keyword to search for in log messages."
                }
            },
            "required": ["service", "keyword"]
        }
    },
    {
        "name": "get_metric",
        "description": "Get a metric value for a service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Name of the service."
                },
                "metric_name": {
                    "type": "string",
                    "description": "Name of the metric to retrieve."
                }
            },
            "required": ["service", "metric_name"]
        }
    },
    {
        "name": "get_recent_deployments",
        "description": "Get recent deployments for a service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Name of the service."
                }
            },
            "required": ["service"]
        }
    },
    {
        "name": "get_service_health",
        "description": "Get the current health status of a service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Name of the service."
                }
            },
            "required": ["service"]
        }
    }
]

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def ask_claude(service: str, description: str):
    message = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=500,
        tools=TOOLS,
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