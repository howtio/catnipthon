"""Interactive REPL for catnip-agent — thread pool + Claude Code-style output."""

from __future__ import annotations

import os
import sys
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from src.shared.types import RunTask
from src.shared.cli import (
    W, H_LINE, SYM_SUB, SYM_OK,
    _c, DIM, OK, ERROR, HIGHLIGHT,
    print_divider, print_step_claude, print_result_claude,
    print_summary_claude, print_thinking, print_user_message,
)
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
    /stop                 Cancel the currently running task
    /inject <msg>         Inject a message into the running agent
    Any text typed while agent is running is auto-injected.
{'-' * W}
"""

_print_lock = threading.Lock()


def _safe_print(text: str) -> None:
    """Thread-safe print with GBK fallback."""
    with _print_lock:
        try:
            print(text)
        except UnicodeEncodeError:
            enc = sys.stdout.encoding or "utf-8"
            safe = text.encode(enc, errors="replace").decode(enc, errors="replace")
            print(safe)


class ProgressTracker:
    """Claude Code-style progress tracker for background task execution.

    Subscribes to EventBus events from the background agent thread
    and prints them in Claude Code format using a thread-safe lock.
    """

    def __init__(self, eventbus: EventBusLayerApi) -> None:
        self._eventbus = eventbus
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

    def start(self) -> None:
        """Subscribe to EventBus events."""
        self._start_time = time.time()
        self._unsubs.append(
            self._eventbus.subscribe(event_types.TOOL_CALL_REQUESTED, self._on_tool_call)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.AGENT_STEP_FINISHED, self._on_step_finished)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.LLM_USAGE, self._on_llm_usage)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.RUN_STARTED, self._on_run_started)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.AGENT_REASONING_CHUNK, self._on_reasoning_chunk)
        )
        self._unsubs.append(
            self._eventbus.subscribe(event_types.AGENT_ANSWER_PRODUCED, self._on_answer)
        )

    def stop(self) -> None:
        """Unsubscribe all listeners."""
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()

    def reset(self) -> None:
        """Reset counters for a new run."""
        self.stop()
        self._step_count = 0
        self._total_steps = 0
        self._step_tokens.clear()
        self._tool_counts.clear()
        self._token_usage.clear()
        self._run_id = ""

    def _on_run_started(self, event: Event) -> None:
        self._run_id = event.payload.get("run_id", "")

    def _on_tool_call(self, event: Event) -> None:
        self._step_count += 1
        self._current_tool = event.payload.get("tool_name", "")
        self._step_start = time.time()
        args = event.payload.get("arguments", {})
        args_str = ""
        if args:
            # Show first meaningful arg (file_path or path)
            for key in ("file_path", "path", "command"):
                val = args.get(key, "")
                if val:
                    args_str = f"{key}: {str(val)[:60]}"
                    break
        _safe_print("")  # spacing
        with _print_lock:
            print_step_claude(self._step_count, self._current_tool, args_str)

    def _on_step_finished(self, event: Event) -> None:
        tool = event.payload.get("tool", "")
        success = event.payload.get("success", False)
        duration = time.time() - self._step_start if self._step_start else 0
        tokens = self._step_tokens.get(self._step_count, 0)
        with _print_lock:
            print_result_claude(success, duration, tokens)
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

    def _on_reasoning_chunk(self, event: Event) -> None:
        chunk = event.payload.get("chunk", "")
        elapsed = event.payload.get("elapsed_s", 0)
        heartbeat = event.payload.get("heartbeat", False)
        with _print_lock:
            print_thinking(chunk, elapsed_s=elapsed, heartbeat=heartbeat)

    def _on_answer(self, event: Event) -> None:
        total_duration = (time.time() - self._start_time) * 1000
        with _print_lock:
            print_summary_claude(
                steps=self._step_count or 1,
                duration_ms=total_duration,
                token_usage=self._token_usage,
                tool_counts=dict(self._tool_counts),
            )


def _run_task_in_thread(
    app: App,
    task: RunTask,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    """Run a task via harness in the background thread."""
    try:
        result = app.harness.run(task, conversation_history=conversation_history)
        return result
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"


def _truncate_display(result: str) -> str:
    """Truncate long output for display."""
    display = result.strip()
    if "## Result" in display:
        display = display.split("## Result", 1)[-1].strip()
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
    return "\n".join(short_lines)


def _print_result_display(result: str) -> None:
    """Print the final result in clean format."""
    _safe_print("")
    print_divider("Result")
    display = _truncate_display(result)
    for line in display.split("\n"):
        _safe_print(f"  {line}")
    print_divider()


def run_interactive(app: App) -> None:
    """Run the interactive REPL with background task execution.

    Tasks run in a ThreadPoolExecutor so the user can inject requirements
    while the agent is working.
    """
    executor = ThreadPoolExecutor(max_workers=1)
    current_task: RunTask | None = None
    current_future: Future[Any] | None = None
    conversation_history: list[dict[str, str]] = []
    tracker = ProgressTracker(app.eventbus)
    provider = os.environ.get("CATNIP_RUNNER_PROVIDER", "deepseek")

    # Restore previous conversation history
    saved = app.memory.get_conversation_history(max_turns=20)
    if saved:
        conversation_history = list(saved)

    print(f"  Type /help for commands, /exit to quit.")
    print(f"  Provider: {provider}  |  Turns: {len(conversation_history) // 2}")
    print()

    while True:
        # Check if a background task just completed
        if current_future is not None and current_future.done():
            try:
                result = current_future.result()
                _print_result_display(result)

                # Save to conversation history
                answer_text = _truncate_display(result)[:500]
                conversation_history.append({"role": "user", "content": current_task.user_message if current_task else ""})
                conversation_history.append({"role": "assistant", "content": answer_text})
                if len(conversation_history) > 40:
                    conversation_history = conversation_history[-40:]
                app.memory.set_conversation_history(conversation_history)
            except Exception as e:
                _safe_print(f"  {SYM_SUB} {_c(f'Task failed: {e}', ERROR)}")

            current_future = None
            current_task = None
            tracker.stop()

        # Read user input
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            _safe_print("")
            _safe_print(f"  {SYM_SUB} Bye!")
            break

        if not raw:
            continue

        # ── Internal commands ──
        if raw in ("/exit", "/quit"):
            # If a task is running, wait for it to finish
            if current_future is not None and not current_future.done():
                _safe_print(f"  {SYM_SUB} Waiting for task to finish...")
            _safe_print(f"  {SYM_SUB} Bye!")
            break

        if raw == "/help":
            _safe_print(HELP_TEXT)
            continue

        if raw == "/clear":
            os.system("cls" if os.name == "nt" else "clear")
            continue

        if raw == "/new":
            conversation_history.clear()
            app.memory.clear_session()
            _safe_print(f"  {SYM_SUB} Conversation cleared.")
            continue

        if raw == "/history":
            events = app.eventbus.get_history()
            for evt in events[-10:]:
                _safe_print(f"  {evt.type}: {str(evt.payload)[:80]}")
            continue

        if raw == "/provider":
            _safe_print(f"  Provider: {provider}")
            continue

        if raw.startswith("/provider "):
            new_provider = raw[len("/provider "):].strip()
            if new_provider in ("heuristic", "deepseek"):
                os.environ["CATNIP_RUNNER_PROVIDER"] = new_provider
                provider = new_provider
                _safe_print(f"  {SYM_SUB} Provider switched to: {provider}")
            else:
                _safe_print(f"  Unknown provider: {new_provider}")
            continue

        # ── If a task is currently running, inject ──
        if current_future is not None and not current_future.done():
            if raw.startswith("/inject "):
                msg = raw[len("/inject "):].strip()
            elif raw.startswith("/"):
                _safe_print(f"  Unknown command: {raw}")
                continue
            elif raw == "/stop":
                _safe_print(f"  {SYM_SUB} Cancelling task...")
                current_future.cancel()
                continue
            else:
                msg = raw

            if msg and current_task:
                app.queue.append_requirement(current_task.id, msg)
                _safe_print(f"  {SYM_SUB} {_c('Injected:', DIM)} {msg[:60]}")
            continue

        # ── Start a new task ──
        if raw.startswith("/"):
            _safe_print(f"  Unknown command: {raw}")
            continue

        current_task = RunTask(id=os.urandom(4).hex(), user_message=raw)
        app.queue.enqueue(current_task)

        # Show user message in Claude Code style
        print_user_message(raw)

        # Start tracker for this run
        tracker.reset()
        tracker.start()

        # Submit to thread pool
        current_future = executor.submit(
            _run_task_in_thread, app, current_task, conversation_history
        )

        # Small delay to let ProgressTracker output appear
        time.sleep(0.1)

    executor.shutdown(wait=False)
