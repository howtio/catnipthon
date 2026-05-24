"""DeepSeek provider using the OpenAI SDK to call DeepSeek's API with streaming."""

from __future__ import annotations

import json
import os
import time
from typing import Any

from openai import OpenAI

from src.shared.types import RunTask
from src.layers.runner_08.types import RunnerConfig
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.tool_registry_10 import ToolRegistryLayerApi


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
_THINKING_TIMEOUT = 5.0  # publish heartbeat every N seconds during long thinking


def _get_client() -> OpenAI | None:
    """Create an OpenAI client pointing to DeepSeek API."""
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        return None
    return OpenAI(api_key=key, base_url=DEEPSEEK_BASE_URL)


def _stream_and_collect(
    client: OpenAI,
    kwargs: dict[str, Any],
    eventbus: EventBusLayerApi,
    step_count: int,
) -> tuple[str, list[dict[str, Any]] | None, dict[str, int] | None]:
    """Stream a chat completion, publishing reasoning chunks in real-time.

    Returns (full_content, tool_calls_list, usage_dict).
    """
    stream = client.chat.completions.create(**kwargs)
    full_content = ""
    tool_calls_acc: dict[int, dict[str, Any]] = {}
    usage: dict[str, int] | None = None
    thinking_start = time.time()
    last_heartbeat = thinking_start

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

        # ── Real-time reasoning content ──
        reasoning = getattr(delta, "reasoning_content", None)
        if reasoning:
            now = time.time()
            elapsed = now - thinking_start
            eventbus.publish(event_types.AGENT_REASONING_CHUNK, {
                "chunk": reasoning,
                "step": step_count,
                "elapsed_s": round(elapsed, 1),
            })
            last_heartbeat = now

        # ── Content (final answer or tool call preamble) ──
        if delta.content:
            full_content += delta.content

        # ── Streaming tool calls ──
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

        # ── Thinking heartbeat — publish a timer every few seconds ──
        if not reasoning and not delta.content and not delta.tool_calls:
            now = time.time()
            if now - last_heartbeat >= _THINKING_TIMEOUT:
                elapsed = now - thinking_start
                eventbus.publish(event_types.AGENT_REASONING_CHUNK, {
                    "chunk": "",
                    "step": step_count,
                    "elapsed_s": round(elapsed, 1),
                    "heartbeat": True,
                })
                last_heartbeat = now

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
    """Run the agent with DeepSeek reasoner model and tool calling (streaming).

    Reasoning content is published chunk-by-chunk as AGENT_REASONING_CHUNK
    so the CLI can display it in real-time. After streaming completes, any
    tool calls are executed and the loop continues.
    """
    client = _get_client()
    if client is None:
        return "[deepseek] No DEEPSEEK_API_KEY set. Use provider='heuristic'."

    cfg = config or RunnerConfig()
    messages: list[dict[str, Any]] = []

    # deepseek-reasoner does not support system messages natively;
    # prepend system prompt as a user message, then conversation history.
    if system_prompt:
        messages.append({"role": "user", "content": system_prompt})

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({"role": "user", "content": task.user_message})

    tools = registry.to_openai_schemas()
    tool_choice = "auto" if tools else None

    step_count = 0
    max_steps = cfg.max_steps

    eventbus.publish(event_types.AGENT_PLAN_GENERATED, {
        "plan": [],
        "step_count": 0,
        "provider": "deepseek",
    })

    while step_count < max_steps:
        step_count += 1

        try:
            kwargs: dict[str, Any] = {
                "model": "deepseek-reasoner",
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

        # Publish reasoning summary
        reasoning_preview = (content or "")[:500]
        eventbus.publish(event_types.AGENT_REASONING_SUMMARY, {
            "steps_completed": step_count,
            "final_reasoning": reasoning_preview,
        })

        if not tools or not tool_calls_list:
            answer = content or "(no response)"
            eventbus.publish(event_types.AGENT_ANSWER_PRODUCED, {"answer": answer})
            return answer

        # Reconstruct assistant message with tool calls
        assistant_msg: dict[str, Any] = {"role": "assistant", "content": content or ""}
        assistant_msg["tool_calls"] = tool_calls_list
        messages.append(assistant_msg)

        # Execute each tool call
        tool_results: list[dict[str, Any]] = []
        for tc in tool_calls_list:
            fn_name = tc["function"]["name"]
            try:
                fn_args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                fn_args = {}

            tool_call_id = tc["id"]

            eventbus.publish(event_types.TOOL_CALL_REQUESTED, {
                "tool_call_id": tool_call_id,
                "tool_name": fn_name,
                "arguments": fn_args,
                "step": step_count,
            })

            result_payload = eventbus.wait_for_tool_result(tool_call_id, timeout=30.0)

            if result_payload is None:
                tool_result_msg = f"Error: tool {fn_name} timed out"
            elif result_payload.get("error"):
                tool_result_msg = f"Error: {result_payload['error']}"
            else:
                tool_result_msg = result_payload.get("output", "(no output)")

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
