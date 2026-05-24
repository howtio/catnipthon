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


def _stream_chunk(content: str = "", reasoning: str | None = None,
                  tool_calls: list | None = None,
                  usage: object | None = None) -> MagicMock:
    """Build a mock streaming chunk."""
    delta = MagicMock()
    delta.content = content
    delta.reasoning_content = reasoning
    delta.tool_calls = tool_calls
    choice = MagicMock()
    choice.delta = delta
    chunk = MagicMock()
    chunk.choices = [choice]
    chunk.usage = usage
    return chunk


def _usage(prompt: int = 10, comp: int = 5, total: int = 15) -> MagicMock:
    u = MagicMock()
    u.prompt_tokens = prompt
    u.completion_tokens = comp
    u.total_tokens = total
    return u


def _make_stream(*chunks: MagicMock) -> MagicMock:
    """Return iterable mock chunks ending with a usage chunk."""
    usage_chunk = MagicMock()
    usage_chunk.choices = []
    usage_chunk.usage = _usage()
    # Return a list so iteration works (list iterator)
    return list(chunks) + [usage_chunk]


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

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_stream(
        _stream_chunk(content="Hello, world!", reasoning="thinking..."),
    )

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

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_stream(
        _stream_chunk(content="OK"),
    )

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
    # streaming mode
    assert call_kwargs.get("stream") is True


def test_max_steps_exceeded() -> None:
    task = RunTask(id="t5", user_message="hello")
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    cfg = RunnerConfig(max_steps=2)

    # Mock streaming tool call
    mock_tc = MagicMock()
    mock_tc.index = 0
    mock_tc.id = "call_1"
    mock_tc.function.name = "list_files"
    mock_tc.function.arguments = '{"path": "."}'

    mock_client = MagicMock()
    # Both API calls return a stream with a tool call
    mock_client.chat.completions.create.return_value = _make_stream(
        _stream_chunk(content="", tool_calls=[mock_tc]),
    )

    with patch(
        "src.layers.runner_08.deepseek_provider._get_client",
        return_value=mock_client,
    ):
        with patch.object(eventbus, "wait_for_tool_result", return_value={"output": "OK"}):
            result = run_deepseek(task, eventbus, registry, config=cfg)

    assert "[deepseek] Reached max steps" in result
