"""Interactive REPL for catnip-agent."""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Callable
from typing import Any

from src.shared.types import RunTask
from src.shared.cli import W
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.eventbus_09.types import Event
from src.bootstrap import App


HELP_TEXT = f"""
{'─' * W}
  Commands:
    /exit, /quit          Exit the interactive session
    /help                 Show this help
    /provider             Show current provider
    /provider deepseek    Switch to DeepSeek provider
    /provider heuristic   Switch to heuristic provider
    /history              Show last 10 events
    /clear                Clear the screen
    Anything else is sent to the agent as a task.
{'─' * W}
"""


def _print_boxed(text: str, char: str = "─") -> None:
    print(f"\n{char * W}")
    try:
        print(text)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "utf-8"
        safe = text.encode(enc, errors="replace").decode(enc, errors="replace")
        print(safe)
    print(f"{char * W}")


def _render_progress_bar(current: int, total: int, width: int = 20) -> str:
    filled = int(width * current / total) if total > 0 else 0
    bar = "#" * filled + "." * (width - filled)
    return f"[{bar}] {current}/{total}"


class ProgressTracker:
    """Subscribes to EventBus and prints real-time progress during a task."""

    def __init__(self, eventbus: EventBusLayerApi) -> None:
        self._eventbus = eventbus
        self._unsubs: list[Callable[[], None]] = []
        self._step_count = 0
        self._total_steps = 0
        self._start_time = 0.0

    def __enter__(self) -> ProgressTracker:
        self._start_time = time.time()
        self._unsubs.append(
            self._eventbus.subscribe(event_types.TOOL_CALL_REQUESTED, self._on_tool_call)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.TOOL_CALL_RESULT, self._on_tool_result)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.TOOL_CALL_FAILED, self._on_tool_failed)
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
        return self

    def __exit__(self, *args: Any) -> None:
        for unsub in self._unsubs:
            unsub()

    def _on_plan(self, event: Event) -> None:
        plan = event.payload.get("plan", [])
        self._total_steps = len(plan)
        if self._total_steps > 0:
            print(f"  Plan: {self._total_steps} step(s)")

    def _on_tool_call(self, event: Event) -> None:
        self._step_count += 1
        tool_name = event.payload.get("tool_name", "")
        print(f"\n  >> [{self._step_count}] calling {tool_name}...")

    def _on_tool_result(self, event: Event) -> None:
        tool_name = event.payload.get("tool_name", "")
        elapsed = (time.time() - self._start_time) * 1000
        print(f"     done ({elapsed:.0f}ms)")

    def _on_tool_failed(self, event: Event) -> None:
        tool_name = event.payload.get("tool_name", "")
        error = event.payload.get("error", "")
        print(f"     [!] {tool_name} failed: {error}")

    def _on_step_finished(self, event: Event) -> None:
        step = event.payload.get("step", 0)
        tool = event.payload.get("tool", "")
        success = event.payload.get("success", False)
        mark = "[ok]" if success else "[!!]"
        if self._total_steps > 0:
            bar = _render_progress_bar(step + 1, self._total_steps)
            print(f"  {mark} Step {step + 1}/{self._total_steps}  {bar}")
        else:
            print(f"  {mark} Step {step + 1}")

    def _on_answer(self, event: Event) -> None:
        elapsed = (time.time() - self._start_time) * 1000
        print(f"\n  Answer received ({elapsed:.0f}ms)")


def run_interactive(app: App) -> None:
    """Run the interactive REPL."""
    current_provider = os.environ.get("CATNIP_RUNNER_PROVIDER", "heuristic")

    print()
    print(f"  Type /help for commands, /exit to quit.")
    print(f"  Provider: {current_provider}")
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
                generate_reply_if_deepseek(current_provider)
            else:
                print(f"  Unknown provider: {new_provider} (use heuristic or deepseek)")
            continue

        if raw.startswith("/"):
            print(f"  Unknown command: {raw} (try /help)")
            continue

        # Run the task
        with ProgressTracker(app.eventbus):
            start = time.time()
            try:
                result = app.gateway.run_cli([raw])
                elapsed = (time.time() - start) * 1000
            except Exception as e:
                print(f"\n  [!] Error: {e}")
                continue

        _print_boxed(result.strip())


def generate_reply_if_deepseek(provider: str) -> None:
    """print something when switching to deepseek."""
    if provider == "deepseek":
        key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not key:
            print("  [!] DEEPSEEK_API_KEY not set. DeepSeek will fallback to heuristic.")
        else:
            print("  DeepSeek API key detected.")
