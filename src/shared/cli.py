"""Catnip CLI rendering — reusable scaffolding component.

Import `BANNER`, `LAYERS`, `print_header`, `print_task_bar`,
`print_result_ok`, `print_result_fail` from here.
Other projects using this scaffolding can override `TITLE` and `SUBTITLE`.
"""

from __future__ import annotations

from src.shared.version import VERSION, VERSION_TAG

W = 46  # internal box width (between border chars)

TITLE = "catnip agent"
SUBTITLE = "11-Layer Coding Agent Runtime"

LAYERS = (
    "gateway_01  →  queue_02    →  worker_03\n"
    "harness_04  →  context_05  →  skills_06\n"
    "memory_07   →  runner_08   →  eventbus_09\n"
    "tool_registry_10 → executor_11"
)


def _pad_center(text: str, width: int = W) -> str:
    return text.center(width)


BANNER = f"""╔{'═' * W}╗
║{_pad_center('')}║
║{_pad_center(TITLE + '  ' + VERSION_TAG)}║
║{_pad_center(SUBTITLE)}║
║{_pad_center('')}║
╠{'═' * W}╣
║{'Layers'.center(W)}║
╠{'═' * W}╣"""

BANNER_BOTTOM = f"╚{'═' * W}╝"


def _layer_lines() -> list[str]:
    return ["║" + line.center(W) + "║" for line in LAYERS.split("\n")]


def print_header() -> None:
    print(BANNER)
    for line in _layer_lines():
        print(line)
    print(BANNER_BOTTOM)


def print_task_bar(user_message: str) -> None:
    print(f"\n{'─' * W}")
    print(f"  Task: {user_message}")
    print(f"{'─' * W}")


def print_result_ok(task_id: str, result: str) -> None:
    print(f"\n  [OK] Task {task_id} completed")
    print(f"{'─' * W}")
    print(result)
    print(f"{'─' * W}")


def print_result_fail(task_id: str, error: str | None) -> None:
    print(f"\n  [!] Task {task_id} failed")
    if error:
        print(f"  Error: {error}")
