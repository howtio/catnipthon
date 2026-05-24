"""Catnip CLI rendering — reusable scaffolding component.

Import `BANNER`, `LAYERS`, `print_header`, `print_task_bar`,
`print_result_ok`, `print_result_fail` from here.
Other projects using this scaffolding can override `TITLE` and `SUBTITLE`.
"""

from __future__ import annotations

from src.shared.version import VERSION, VERSION_TAG

W = 46  # internal box width (between border chars)
H_LINE = "\u2500" * W
EQUAL_LINE = "=" * W

TITLE = "catnip agent"
SUBTITLE = "11-Layer Coding Agent Runtime"

LAYERS = (
    "gateway_01  \u2192  queue_02    \u2192  worker_03\n"
    "harness_04  \u2192  context_05  \u2192  skills_06\n"
    "memory_07   \u2192  runner_08   \u2192  eventbus_09\n"
    "tool_registry_10 \u2192 executor_11"
)


def _pad_center(text: str, width: int = W) -> str:
    return text.center(width)


BANNER = f"""\u255e{'═' * W}\u255d
\u2551{_pad_center('')}\u2551
\u2551{_pad_center(TITLE + '  ' + VERSION_TAG)}\u2551
\u2551{_pad_center(SUBTITLE)}\u2551
\u2551{_pad_center('')}\u2551
\u2560{'═' * W}\u2563
\u2551{'Layers'.center(W)}\u2551
\u2560{'═' * W}\u2563"""

BANNER_BOTTOM = f"\u255a{'═' * W}\u255d"


def _layer_lines() -> list[str]:
    return ["\u2551" + line.center(W) + "\u2551" for line in LAYERS.split("\n")]


def print_header() -> None:
    print(BANNER)
    for line in _layer_lines():
        print(line)
    print(BANNER_BOTTOM)


def print_task_bar(user_message: str) -> None:
    print(f"\n{H_LINE}")
    print(f"  Task: {user_message}")
    print(H_LINE)


def print_result_ok(task_id: str, result: str) -> None:
    print(f"\n  [OK] Task {task_id} completed")
    print(H_LINE)
    print(result)
    print(H_LINE)


def print_result_fail(task_id: str, error: str | None) -> None:
    print(f"\n  [!] Task {task_id} failed")
    if error:
        print(f"  Error: {error}")
