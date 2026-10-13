import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from app.agent import ask_claude


def test_agent_executes_tool_and_returns_report():
    # Simulate Claude requesting a diagnostic tool.
    tool_request = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="tool_use",
                id="tool_123",
                name="get_service_health",
                input={"service": "checkout"},
            )
        ]
    )

    # Simulate Claude's final investigation.
    final_report = {
        "severity": "high",
        "likely_root_cause": "Checkout service is unhealthy",
        "evidence": ["Service health check failed"],
        "recommended_actions": ["Investigate service health"],
    }

    final_response = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="text",
                text=json.dumps(final_report),
            )
        ]
    )

    # Replace Claude and the diagnostic tool with mocks.
    with (
        patch("app.agent.client.messages.create") as mock_create,
        patch.dict("app.agent.TOOL_FUNCTIONS") as mock_tools,
    ):
        mock_create.side_effect = [
            tool_request,
            final_response,
        ]

        mock_health = Mock(
            return_value={
                "service": "checkout",
                "status": "unhealthy",
            }
        )

        mock_tools["get_service_health"] = mock_health

        # Run the actual agent logic.
        report = ask_claude(
            service="checkout",
            description="Checkout is returning 500 errors",
        )

        # Verify the correct diagnostic tool was called.
        mock_health.assert_called_once_with(
            service="checkout"
        )

        # Verify Claude was called twice.
        assert mock_create.call_count == 2

        # Verify the tool result was sent back to Claude.
        second_call = mock_create.call_args_list[1]
        messages = second_call.kwargs["messages"]

        tool_results = messages[2]["content"]

        assert tool_results[0]["type"] == "tool_result"
        assert tool_results[0]["tool_use_id"] == "tool_123"

        result = json.loads(tool_results[0]["content"])

        assert result["status"] == "unhealthy"

        # Verify the structured report.
        assert report.severity == "high"
        assert report.likely_root_cause == (
            "Checkout service is unhealthy"
        )


def test_agent_rejects_invalid_json():
    # Simulate Claude returning invalid JSON.
    invalid_response = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="text",
                text="This is not valid JSON",
            )
        ]
    )

    # Verify the agent rejects the invalid response.
    with patch(
        "app.agent.client.messages.create",
        return_value=invalid_response,
    ):
        with pytest.raises(ValueError):
            ask_claude(
                service="checkout",
                description="Checkout is returning 500 errors",
            )


def test_agent_stops_after_max_iterations():
    # Simulate Claude repeatedly requesting the same tool.
    tool_request = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="tool_use",
                id="tool_123",
                name="get_service_health",
                input={"service": "checkout"},
            )
        ]
    )

    with (
        patch(
            "app.agent.client.messages.create",
            return_value=tool_request,
        ) as mock_create,
        patch.dict("app.agent.TOOL_FUNCTIONS") as mock_tools,
    ):
        mock_health = Mock(
            return_value={
                "service": "checkout",
                "status": "unhealthy",
            }
        )
        mock_tools["get_service_health"] = mock_health

        # The agent should stop after its iteration limit.
        with pytest.raises(
            RuntimeError,
            match="Agent exceeded maximum investigation iterations",
        ):
            ask_claude(
                service="checkout",
                description="Checkout is returning 500 errors",
            )

        # Verify Claude was called exactly MAX_ITERATIONS times.
        from app.agent import MAX_ITERATIONS

        assert mock_create.call_count == MAX_ITERATIONS
        assert mock_health.call_count == MAX_ITERATIONS