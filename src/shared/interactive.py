"""Interactive REPL for catnip-agent — continuous conversation mode."""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Callable
from typing import Any

from src.shared.types import RunTask
from src.shared.cli import W, H_LINE, _c, print_step_header, print_step_result, print_session_summary
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.eventbus_09.types import Event
from src.bootstrap import App


HELP_TEXT = f"""
{'-' * W}
  Commands:
    /exit, /quit          Exit the interactive session
    /help                 Show this help
    /provider             Show current provider
    /provider deepseek    Switch to DeepSeek provider
    /provider heuristic   Switch to heuristic provider
    /history              Show last 10 events
    /clear                Clear the screen
    /new                  Start a fresh conversation (clear history)
    /inject <msg>         Inject a message into the running agent
    Anything else is sent to the agent as part of an ongoing conversation.
{'-' * W}
"""


def _print_boxed(text: str, char: str = "-") -> None:
    print(f"\n{char * W}")
    try:
        print(text)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "utf-8"
        safe = text.encode(enc, errors="replace").decode(enc, errors="replace")
        print(safe)
    print(f"{char * W}")


class ProgressTracker:
    """Codex-style progress tracker with per-step timing and token display.

    Also handles mid-task user input injection by subscribing to
    AGENT_ASKING_USER and prompting the user inline.
    """

    def __init__(self, eventbus: EventBusLayerApi, user_input_queue: list[str]) -> None:
        self._eventbus = eventbus
        self._user_input_queue = user_input_queue
        self._unsubs: list[Callable[[], None]] = []
        self._step_count = 0
        self._total_steps = 0
        self._start_time = 0.0
        self._step_start: float = 0.0
        self._current_tool = ""
        self._step_tokens: dict[int, int] = {}
        self._run_id = ""
        self._tool_counts: dict[str, int] = {}
        self._token_usage: dict[str, int] = {}

    def __enter__(self) -> ProgressTracker:
        self._start_time = time.time()
        self._unsubs.append(
            self._eventbus.subscribe(event_types.TOOL_CALL_REQUESTED, self._on_tool_call)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.AGENT_STEP_FINISHED, self._on_step_finished)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.AGENT_PLAN_GENERATED, self._on_plan)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.AGENT_ANSWER_PRODUCED, self._on_answer)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.LLM_USAGE, self._on_llm_usage)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.RUN_STARTED, self._on_run_started)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.AGENT_ASKING_USER, self._on_asking_user)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.AGENT_REASONING_CHUNK, self._on_reasoning_chunk)
        )
        return self

    def __exit__(self, *args: Any) -> None:
        for unsub in self._unsubs:
            unsub()

    def _on_run_started(self, event: Event) -> None:
        self._run_id = event.payload.get("run_id", "")

    def _on_plan(self, event: Event) -> None:
        plan = event.payload.get("plan", [])
        self._total_steps = len(plan)
        if self._total_steps > 0:
            print(f"\n  Plan: {self._total_steps} step(s)")
            print(f"  {'-' * (W - 2)}")

    def _on_tool_call(self, event: Event) -> None:
        self._step_count += 1
        self._current_tool = event.payload.get("tool_name", "")
        self._step_start = time.time()
        print_step_header(self._step_count, self._total_steps or self._step_count, self._current_tool)

    def _on_step_finished(self, event: Event) -> None:
        step = event.payload.get("step", 0)
        tool = event.payload.get("tool", "")
        success = event.payload.get("success", False)
        duration = time.time() - self._step_start if self._step_start else 0
        tokens = self._step_tokens.get(self._step_count, 0)
        print_step_result(success, duration, tokens)
        self._tool_counts[tool] = self._tool_counts.get(tool, 0) + 1

    def _on_llm_usage(self, event: Event) -> None:
        step = event.payload.get("step", 0)
        tokens = event.payload.get("total_tokens", 0) or 0
        self._step_tokens[step] = self._step_tokens.get(step, 0) + tokens
        self._token_usage = {
            "prompt_tokens": self._token_usage.get("prompt_tokens", 0) + (event.payload.get("prompt_tokens", 0) or 0),
            "completion_tokens": self._token_usage.get("completion_tokens", 0) + (event.payload.get("completion_tokens", 0) or 0),
            "total_tokens": self._token_usage.get("total_tokens", 0) + tokens,
        }

    def _on_asking_user(self, event: Event) -> None:
        """Agent is asking for user input. Check the queue for any pending input."""
        if self._user_input_queue:
            msg = self._user_input_queue.pop(0)
            print(f"  [注入] 检测到追加要求...")
            self._eventbus.publish(event_types.AGENT_USER_RESPONSE, {
                "input": msg,
                "injected": False,
            })

    def _on_reasoning_chunk(self, event: Event) -> None:
        """Display DeepSeek reasoning content in real-time."""
        chunk = event.payload.get("chunk", "")
        if chunk:
            print(f"\r  {_c(chunk[:120], 96)}", end="")

    def _on_answer(self, event: Event) -> None:
        total_duration = (time.time() - self._start_time) * 1000
        print_session_summary(
            run_id=self._run_id,
            steps=self._step_count,
            duration_ms=total_duration,
            token_usage=self._token_usage,
            tool_summary=dict(self._tool_counts),
        )


def run_interactive(app: App) -> None:
    """Run the interactive REPL with continuous conversation and mid-task injection."""
    current_provider = os.environ.get("CATNIP_RUNNER_PROVIDER", "deepseek")
    conversation_history: list[dict[str, str]] = []
    user_input_queue: list[str] = []

    # Restore previous conversation history from memory
    saved = app.memory.get_conversation_history(max_turns=20)
    if saved:
        conversation_history = list(saved)

    print()
    print(f"  Type /help for commands, /exit to quit.")
    print(f"  Provider: {current_provider}")
    print(f"  Conversation turns: {len(conversation_history) // 2}")
    print()

    while True:
        try:
            raw = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print("  Bye!")
            break

        if not raw:
            continue

        # Internal commands
        if raw in ("/exit", "/quit"):
            print("  Bye!")
            break

        if raw == "/help":
            _print_boxed(HELP_TEXT)
            continue

        if raw == "/clear":
            os.system("cls" if os.name == "nt" else "clear")
            continue

        if raw == "/new":
            conversation_history.clear()
            app.memory.clear_session()
            user_input_queue.clear()
            print("  Conversation history cleared. Starting fresh.")
            continue

        if raw == "/history":
            events = app.eventbus.get_history()
            _print_boxed("\n".join(f"  {e.type}: {e.payload}" for e in events[-10:]))
            continue

        if raw == "/provider":
            print(f"  Current provider: {current_provider}")
            continue

        if raw.startswith("/provider "):
            new_provider = raw[len("/provider "):].strip()
            if new_provider in ("heuristic", "deepseek"):
                os.environ["CATNIP_RUNNER_PROVIDER"] = new_provider
                current_provider = new_provider
                print(f"  Provider switched to: {current_provider}")
                _check_deepseek_key(current_provider)
            else:
                print(f"  Unknown provider: {new_provider} (use heuristic or deepseek)")
            continue

        if raw.startswith("/inject "):
            inject_msg = raw[len("/inject "):].strip()
            if inject_msg:
                user_input_queue.append(inject_msg)
                print(f"  [!] 追加要求已加入队列: \"{inject_msg[:60]}\"")
                print(f"      等待 agent 检测后注入...")
            else:
                print("  [!] 用法: /inject <追加要求>")
            continue

        if raw.startswith("/"):
            print(f"  Unknown command: {raw} (try /help)")
            continue

        # Run the task with conversation history
        task = RunTask(id="", user_message=raw)

        with ProgressTracker(app.eventbus, user_input_queue):
            try:
                if conversation_history:
                    result = app.harness.run(task, conversation_history=conversation_history)
                else:
                    result = app.harness.run(task)
            except Exception as e:
                print(f"\n  [!] Error: {e}")
                continue

        # Display the result — strip report header, truncate long file dumps
        print(f"\n{H_LINE}")
        display = result.strip()
        if "## Result" in display:
            display = display.split("## Result", 1)[-1].strip()
        # Truncate long lines (raw file content) and cap total output
        lines = display.split("\n")
        short_lines: list[str] = []
        for line in lines:
            if len(line) > 200:
                short_lines.append(line[:100] + " ... (truncated) ... " + line[-40:])
            else:
                short_lines.append(line)
        if len(short_lines) > 50:
            short_lines = short_lines[:48]
            short_lines.append("  ... (output truncated, too many lines)")
        display = "\n".join(short_lines)
        try:
            print(display)
        except UnicodeEncodeError:
            enc = sys.stdout.encoding or "utf-8"
            safe = display.encode(enc, errors="replace").decode(enc, errors="replace")
            print(safe)
        print(H_LINE)

        # Save to conversation history (use truncated version)
        answer_text = "\n".join(short_lines[:10])
        if len(short_lines) > 10:
            answer_text += "\n  ... (output truncated)"
        conversation_history.append({"role": "user", "content": raw})
        conversation_history.append({"role": "assistant", "content": answer_text})
        # Keep only last 20 turns (40 messages)
        if len(conversation_history) > 40:
            conversation_history = conversation_history[-40:]
        app.memory.set_conversation_history(conversation_history)


def _check_deepseek_key(provider: str) -> None:
    """Check if deepseek key is available."""
    if provider == "deepseek":
        key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not key:
            print("  [!] DEEPSEEK_API_KEY not set. DeepSeek will fallback to heuristic.")
        else:
            print("  DeepSeek API key detected.")
