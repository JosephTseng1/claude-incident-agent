import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

from app.tools import (
    search_logs,
    get_metric,
    get_recent_deployments,
    get_service_health,
)


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
                    "description": "Name of the service to search.",
                },
                "keyword": {
                    "type": "string",
                    "description": "Keyword to search for in log messages.",
                },
            },
            "required": ["service", "keyword"],
        },
    },
    {
        "name": "get_metric",
        "description": "Get a metric value for a service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Name of the service.",
                },
                "metric_name": {
                    "type": "string",
                    "description": "Name of the metric to retrieve.",
                },
            },
            "required": ["service", "metric_name"],
        },
    },
    {
        "name": "get_recent_deployments",
        "description": "Get recent deployments for a service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Name of the service.",
                },
            },
            "required": ["service"],
        },
    },
    {
        "name": "get_service_health",
        "description": "Get the current health status of a service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Name of the service.",
                },
            },
            "required": ["service"],
        },
    },
]


TOOL_FUNCTIONS = {
    "search_logs": search_logs,
    "get_metric": get_metric,
    "get_recent_deployments": get_recent_deployments,
    "get_service_health": get_service_health,
}


MAX_ITERATIONS = 5


client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def ask_claude(service: str, description: str):
    messages = [
        {
            "role": "user",
            "content": (
                f"Investigate this service incident.\n"
                f"Service: {service}\n"
                f"Description: {description}"
            ),
        }
    ]

    for _ in range(MAX_ITERATIONS):
        message = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=2000,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({
            "role": "assistant",
            "content": message.content,
        })

        tool_results = []

        for block in message.content:
            if block.type == "tool_use":
                tool_function = TOOL_FUNCTIONS[block.name]
                result = tool_function(**block.input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        if tool_results:
            messages.append({
                "role": "user",
                "content": tool_results,
            })
            continue

        for block in message.content:
            if block.type == "text":
                return block.text

        raise RuntimeError("Claude returned no text response.")

    raise RuntimeError(
        "Agent exceeded maximum investigation iterations."
    )