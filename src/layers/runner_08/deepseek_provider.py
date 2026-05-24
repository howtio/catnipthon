"""DeepSeek provider using deepseek-chat model with proper function calling."""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from src.shared.types import RunTask
from src.layers.runner_08.types import RunnerConfig
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.tool_registry_10 import ToolRegistryLayerApi


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
_MAX_HISTORY_TOKENS = 12000  # rough char budget for conversation history


def _get_client() -> OpenAI | None:
    """Create an OpenAI client pointing to DeepSeek API."""
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        return None
    return OpenAI(api_key=key, base_url=DEEPSEEK_BASE_URL)


def _truncate(text: str, max_chars: int = 2000) -> str:
    """Truncate long text, keeping start and end visible."""
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return f"{text[:half]}\n... [truncated {len(text) - max_chars} chars] ...\n{text[-half:]}"


def _compress_history(messages: list[dict[str, Any]]) -> None:
    """Compress conversation history in-place to stay within token budget.

    Compresses old tool results (not the last 2 turns) to 500 chars each.
    This is the single biggest token saver for multi-step conversations.
    """
    if len(messages) <= 4:
        return
    # Keep the last 4 messages untouched (system + current exchange), compress older tool results
    compressible = messages[1:-4] if messages[0].get("role") == "system" else messages[:-4]
    for msg in compressible:
        if msg.get("role") == "tool" and msg.get("content"):
            if len(msg["content"]) > 500:
                half = 250
                msg["content"] = (
                    f"{msg['content'][:half]}... [compressed] ...{msg['content'][-half:]}"
                )


def _stream_and_collect(
    client: OpenAI,
    kwargs: dict[str, Any],
    eventbus: EventBusLayerApi,
    step_count: int,
) -> tuple[str, list[dict[str, Any]] | None, dict[str, int] | None]:
    """Stream a chat completion, publishing content chunks in real-time.

    deepseek-chat streams both content and tool_calls similarly to OpenAI.
    Content chunks are published as AGENT_REASONING_CHUNK so the CLI can
    display incremental output. Tool calls are accumulated from streaming
    delta chunks.

    Returns (full_content, tool_calls_list, usage_dict).
    """
    stream = client.chat.completions.create(**kwargs)
    full_content = ""
    tool_calls_acc: dict[int, dict[str, Any]] = {}
    usage: dict[str, int] | None = None

    for chunk in stream:
        # Usage info arrives in the final chunk
        if chunk.usage:
            u = chunk.usage
            usage = {
                "prompt_tokens": u.prompt_tokens or 0,
                "completion_tokens": u.completion_tokens or 0,
                "total_tokens": u.total_tokens or 0,
            }

        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta
        if delta is None:
            continue

        # Stream content chunks for real-time display
        if delta.content:
            full_content += delta.content
            eventbus.publish(event_types.AGENT_REASONING_CHUNK, {
                "chunk": delta.content,
                "step": step_count,
            })

        # Streaming tool calls — same format as OpenAI
        if delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in tool_calls_acc:
                    tool_calls_acc[idx] = {
                        "id": tc.id or "",
                        "type": "function",
                        "function": {"name": "", "arguments": ""},
                    }
                entry = tool_calls_acc[idx]
                if tc.id:
                    entry["id"] = tc.id
                if tc.function:
                    if tc.function.name:
                        entry["function"]["name"] += tc.function.name
                    if tc.function.arguments:
                        entry["function"]["arguments"] += tc.function.arguments

    tool_calls_list = list(tool_calls_acc.values()) if tool_calls_acc else None
    return full_content, tool_calls_list, usage


def run_deepseek(
    task: RunTask,
    eventbus: EventBusLayerApi,
    registry: ToolRegistryLayerApi,
    system_prompt: str = "",
    config: RunnerConfig | None = None,
    conversation_history: list[dict[str, Any]] | None = None,
) -> str:
    """Run the agent with deepseek-chat model and tool calling (streaming).

    deepseek-chat natively supports system messages and OpenAI-compatible
    function calling, unlike deepseek-reasoner. Content is streamed chunk
    by chunk as AGENT_REASONING_CHUNK for real-time display.

    Tool call retries respect RunnerConfig.max_tool_retries.
    Tool results are truncated to 2000 chars to save tokens.
    """
    client = _get_client()
    if client is None:
        return "[deepseek] No DEEPSEEK_API_KEY set. Use provider='heuristic'."

    cfg = config or RunnerConfig()
    messages: list[dict[str, Any]] = []

    # deepseek-chat supports system messages natively
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({"role": "user", "content": task.user_message})

    tools = registry.to_openai_schemas()
    tool_choice = "auto" if tools else None

    step_count = 0
    max_steps = cfg.max_steps
    max_retries = cfg.max_tool_retries

    eventbus.publish(event_types.AGENT_PLAN_GENERATED, {
        "plan": [],
        "step_count": 0,
        "provider": "deepseek",
    })

    while step_count < max_steps:
        step_count += 1

        # Compress history before each API call to manage token budget
        _compress_history(messages)

        try:
            kwargs: dict[str, Any] = {
                "model": "deepseek-chat",
                "messages": messages,
                "max_tokens": 8192,
                "stream": True,
                "stream_options": {"include_usage": True},
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice

            content, tool_calls_list, usage = _stream_and_collect(
                client, kwargs, eventbus, step_count,
            )

            if usage:
                eventbus.publish(event_types.LLM_USAGE, {
                    "step": step_count,
                    **usage,
                    "provider": "deepseek",
                })

        except Exception as e:
            return f"[deepseek] API error: {type(e).__name__}: {e}"

        # No tool calls = final answer
        if not tools or not tool_calls_list:
            answer = content or "(no response)"
            eventbus.publish(event_types.AGENT_ANSWER_PRODUCED, {"answer": answer})
            return answer

        # Reconstruct assistant message with tool calls for conversation context
        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "content": content or "",
        }
        # Ensure tool_calls is formatted per OpenAI conventions
        assistant_msg["tool_calls"] = tool_calls_list
        messages.append(assistant_msg)

        # Execute each tool call (sequential for simplicity)
        tool_results: list[dict[str, Any]] = []
        for tc in tool_calls_list:
            fn_name = tc["function"]["name"]
            fn_args_raw = tc["function"]["arguments"]

            # Parse arguments; on failure send empty dict
            fn_args: dict[str, Any] = {}
            if fn_args_raw:
                try:
                    fn_args = json.loads(fn_args_raw)
                except json.JSONDecodeError:
                    fn_args = {}

            tool_call_id = tc["id"]

            eventbus.publish(event_types.TOOL_CALL_REQUESTED, {
                "tool_call_id": tool_call_id,
                "tool_name": fn_name,
                "arguments": fn_args,
                "step": step_count,
            })

            # Execute with retry support
            result_payload: dict[str, Any] | None = None
            for attempt in range(max_retries):
                result_payload = eventbus.wait_for_tool_result(tool_call_id, timeout=30.0)
                if result_payload is not None and not result_payload.get("error"):
                    break
                if attempt < max_retries - 1:
                    eventbus.publish(event_types.TOOL_CALL_REQUESTED, {
                        "tool_call_id": tool_call_id,
                        "tool_name": fn_name,
                        "arguments": fn_args,
                        "step": step_count,
                        "retry": attempt + 1,
                    })
                    result_payload = eventbus.wait_for_tool_result(tool_call_id, timeout=30.0)

            if result_payload is None:
                tool_result_msg = f"Error: tool {fn_name} timed out after {max_retries} retries"
            elif result_payload.get("error"):
                tool_result_msg = f"Error: {result_payload['error']}"
            else:
                output = result_payload.get("output", "(no output)")
                tool_result_msg = _truncate(output, max_chars=2000)

            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_result_msg,
            })

            eventbus.publish(event_types.AGENT_STEP_FINISHED, {
                "step": step_count,
                "tool": fn_name,
                "success": "error" not in result_payload if result_payload else False,
            })

        messages.extend(tool_results)

        # Inject any queue-appended requirements (thread-safe via TaskStatusStore lock)
        while task.appended_requirements:
            req = task.appended_requirements.pop(0)
            messages.append({"role": "user", "content": f"[追加要求] {req}"})

    msg = f"[deepseek] Reached max steps ({max_steps}) without final answer."
    eventbus.publish(event_types.AGENT_REASONING_SUMMARY, {
        "steps_completed": step_count,
        "final_reasoning": msg,
    })
    eventbus.publish(event_types.AGENT_ANSWER_PRODUCED, {"answer": msg})
    return msg
