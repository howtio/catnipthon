from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.runner_08.deepseek_provider import _get_client, run_deepseek
from src.layers.runner_08.types import RunnerConfig


MODULE = "src.layers.runner_08.deepseek_provider"


def test_no_key_returns_message() -> None:
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}, clear=True):
        task = RunTask(id="t1", user_message="hello")
        eventbus = EventBusLayerApi()
        registry = ToolRegistryLayerApi()
        result = run_deepseek(task, eventbus, registry)
        assert "[deepseek] No DEEPSEEK_API_KEY set" in result


def test_get_client_no_key() -> None:
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}, clear=True):
        client = _get_client()
        assert client is None


def test_get_client_with_key() -> None:
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test"}, clear=True):
        client = _get_client()
        assert client is not None
        assert client.api_key == "sk-test"


def test_api_error_returns_message() -> None:
    task = RunTask(id="t2", user_message="hello")
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    cfg = RunnerConfig(max_steps=1)

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API connection failed")

    with patch(
        "src.layers.runner_08.deepseek_provider._get_client",
        return_value=mock_client,
    ):
        result = run_deepseek(task, eventbus, registry, config=cfg)

    assert "[deepseek] API error" in result
    assert "API connection failed" in result


def test_direct_answer_no_tools() -> None:
    task = RunTask(id="t3", user_message="hello")
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    cfg = RunnerConfig(max_steps=1)

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello, world!"
    mock_response.choices[0].message.tool_calls = None

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch(
        "src.layers.runner_08.deepseek_provider._get_client",
        return_value=mock_client,
    ):
        result = run_deepseek(task, eventbus, registry, config=cfg)

    assert result == "Hello, world!"
    answer_events = eventbus.get_history(event_types.AGENT_ANSWER_PRODUCED)
    assert len(answer_events) == 1
    assert answer_events[0].payload["answer"] == "Hello, world!"


def test_system_prompt_included() -> None:
    task = RunTask(id="t4", user_message="hello")
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    cfg = RunnerConfig(max_steps=1)

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "OK"
    mock_response.choices[0].message.tool_calls = None

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch(
        "src.layers.runner_08.deepseek_provider._get_client",
        return_value=mock_client,
    ):
        run_deepseek(task, eventbus, registry, system_prompt="Be helpful.", config=cfg)

    call_kwargs = mock_client.chat.completions.create.call_args[1]
    messages = call_kwargs["messages"]
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Be helpful."
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "hello"


def test_max_steps_exceeded() -> None:
    task = RunTask(id="t5", user_message="hello")
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    cfg = RunnerConfig(max_steps=2)

    # Mock tool call to keep the loop going
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_1"
    mock_tool_call.function.name = "list_files"
    mock_tool_call.function.arguments = '{"path": "."}'

    mock_response = MagicMock()
    mock_response.choices[0].message.content = ""
    mock_response.choices[0].message.tool_calls = [mock_tool_call]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch(
        "src.layers.runner_08.deepseek_provider._get_client",
        return_value=mock_client,
    ):
        result = run_deepseek(task, eventbus, registry, config=cfg)

    assert "[deepseek] Reached max steps" in result
