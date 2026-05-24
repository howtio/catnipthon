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


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
_USER_INPUT_TIMEOUT = 0.3  # short poll for user input between steps


def _get_client() -> OpenAI | None:
    """Create an OpenAI client pointing to DeepSeek API."""
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        return None
    return OpenAI(api_key=key, base_url=DEEPSEEK_BASE_URL)


def _check_for_user_input(
    eventbus: EventBusLayerApi,
    step_count: int,
    cfg: RunnerConfig,
) -> str | None:
    """Check if user injected input since last step. Returns injected message or None."""
    if not cfg.conversation_mode:
        return None
    if step_count % cfg.check_user_input_every != 0:
        return None

    eventbus.publish(event_types.AGENT_ASKING_USER, {"step": step_count})

    # Check history for any user response published since last step
    events = eventbus.get_history(event_types.AGENT_USER_RESPONSE)
    for evt in reversed(events):
        inp: str = evt.payload.get("input", "") or ""
        injected: bool = evt.payload.get("injected", False) or False
        if inp.strip() and not injected:
            return inp.strip()
    return None


def run_deepseek(
    task: RunTask,
    eventbus: EventBusLayerApi,
    registry: ToolRegistryLayerApi,
    system_prompt: str = "",
    config: RunnerConfig | None = None,
    conversation_history: list[dict[str, Any]] | None = None,
) -> str:
    """Run the agent with DeepSeek model and tool calling.

    If conversation_history is provided, it is prepended so the model
    sees prior turns. In conversation_mode, the loop checks for user
    input injection between steps.
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
                "max_tokens": 4096,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice

            response = client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            msg = choice.message

            # Capture DeepSeek reasoning content
            reasoning = getattr(msg, "reasoning_content", None)
            if reasoning:
                eventbus.publish(event_types.AGENT_REASONING_CHUNK, {
                    "chunk": reasoning,
                    "step": step_count,
                })

            if response.usage:
                eventbus.publish(event_types.LLM_USAGE, {
                    "step": step_count,
                    "prompt_tokens": response.usage.prompt_tokens or 0,
                    "completion_tokens": response.usage.completion_tokens or 0,
                    "total_tokens": response.usage.total_tokens or 0,
                    "provider": "deepseek",
                })

        except Exception as e:
            return f"[deepseek] API error: {type(e).__name__}: {e}"

        if not tools or not msg.tool_calls:
            answer = msg.content or "(no response)"
            eventbus.publish(event_types.AGENT_REASONING_SUMMARY, {
                "steps_completed": step_count,
                "final_reasoning": answer[:500],
            })
            eventbus.publish(event_types.AGENT_ANSWER_PRODUCED, {"answer": answer})
            return answer

        # Append assistant message with tool calls
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

        # Execute each tool call
        tool_results: list[dict[str, Any]] = []
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            try:
                fn_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                fn_args = {}

            tool_call_id = tool_call.id

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

        # Check for user input injection mid-execution
        user_input = _check_for_user_input(eventbus, step_count, cfg)
        if user_input:
            eventbus.publish(event_types.AGENT_USER_RESPONSE, {"input": user_input, "injected": True})
            messages.append({"role": "user", "content": f"[追加要求] {user_input}"})

        # Inject any queue-appended requirements
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
