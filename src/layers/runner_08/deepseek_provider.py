"""DeepSeek provider using the OpenAI SDK to call DeepSeek's API."""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from src.shared.types import RunTask
from src.layers.runner_08.types import RunnerConfig
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.tool_registry_10 import ToolRegistryLayerApi


DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"


def _get_client() -> OpenAI | None:
    """Create an OpenAI client pointing to DeepSeek API."""
    key = DEEPSEEK_API_KEY
    if not key:
        return None
    return OpenAI(api_key=key, base_url=DEEPSEEK_BASE_URL)


def run_deepseek(
    task: RunTask,
    eventbus: EventBusLayerApi,
    registry: ToolRegistryLayerApi,
    system_prompt: str = "",
    config: RunnerConfig | None = None,
) -> str:
    """Run the agent with DeepSeek model and tool calling."""
    client = _get_client()
    if client is None:
        return "[deepseek] No DEEPSEEK_API_KEY set. Use provider='heuristic'."

    cfg = config or RunnerConfig()
    messages: list[dict[str, Any]] = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

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
                "model": "deepseek-chat",
                "messages": messages,
                "max_tokens": 4096,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice

            response = client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            msg = choice.message

        except Exception as e:
            return f"[deepseek] API error: {type(e).__name__}: {e}"

        if not tools or not msg.tool_calls:
            # Final answer
            answer = msg.content or "(no response)"
            eventbus.publish(event_types.AGENT_REASONING_SUMMARY, {
                "steps_completed": step_count,
                "final_reasoning": answer[:500],
            })
            eventbus.publish(event_types.AGENT_ANSWER_PRODUCED, {"answer": answer})
            return answer

        # Process tool calls
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            try:
                fn_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                fn_args = {}

            tool_call_id = tool_call.id

            # Store the assistant message with tool calls
            assistant_msg: dict[str, Any] = {"role": "assistant", "content": msg.content or ""}
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
            messages.append(assistant_msg)

            # Request tool execution via EventBus
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

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_result_msg,
            })

            eventbus.publish(event_types.AGENT_STEP_FINISHED, {
                "step": step_count,
                "tool": fn_name,
                "success": "error" not in result_payload if result_payload else False,
            })

        # Continue loop — model will either call more tools or produce final answer

    msg = f"[deepseek] Reached max steps ({max_steps}) without final answer."
    eventbus.publish(event_types.AGENT_REASONING_SUMMARY, {
        "steps_completed": step_count,
        "final_reasoning": msg,
    })
    eventbus.publish(event_types.AGENT_ANSWER_PRODUCED, {"answer": msg})
    return msg
