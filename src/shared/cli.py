"""Catnip CLI rendering — reusable scaffolding component with ANSI color support.

Import `print_header`, `print_step_header`, `print_step_result`,
`print_session_summary` from here.
"""

from __future__ import annotations

import os
import random
import sys

from src.shared.version import VERSION_TAG

W = 46
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

# ── ANSI color support ──────────────────────────────────────────────────

_COLORS = [92, 93, 94, 95, 96, 32, 33, 34, 35, 36]
_RESET = "\033[0m"
_HAS_COLOR = sys.stdout.isatty() and os.environ.get("TERM") != "dumb"

# Per-layer fixed colors for visual layer identification
LAYER_COLORS: dict[str, int] = {
    "gateway": 95,
    "queue": 94,
    "worker": 93,
    "harness": 92,
    "context": 96,
    "skills": 35,
    "memory": 34,
    "runner": 33,
    "eventbus": 32,
    "tool_registry": 36,
    "executor": 91,
}


def layer_color(layer_name: str) -> int:
    """Return the fixed color code for a given layer name."""
    return LAYER_COLORS.get(layer_name, 37)


def c_layer(text: str, layer_name: str) -> str:
    """Wrap *text* in the fixed color for *layer_name*."""
    return _c(text, layer_color(layer_name))


def _enable_ansi() -> None:
    """Enable ANSI on Windows 10+ consoles."""
    if os.name == "nt":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def _c(text: str, color_code: int | None = None) -> str:
    """Wrap text in ANSI color if terminal supports it."""
    if not _HAS_COLOR:
        return text
    if color_code is None:
        color_code = random.choice(_COLORS)
    return f"\033[{color_code}m{text}{_RESET}"


def _pick() -> int:
    """Return a random color code from the palette."""
    return random.choice(_COLORS)


def _strip_ansi(text: str) -> str:
    """Remove ANSI codes for width calculation."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)


# ── Pink / 256-color support ─────────────────────────────────────────────

PINK = 213  # 256-color pink
BRIGHT_MAGENTA = 95


def _is_256color() -> bool:
    """Check if terminal supports 256-color mode."""
    if not _HAS_COLOR:
        return False
    term = os.environ.get("TERM", "")
    colorterm = os.environ.get("COLORTERM", "")
    return "256" in term or "truecolor" in colorterm or "24bit" in colorterm


def _pink(text: str) -> str:
    """Wrap *text* in pink (256-color) or bright magenta fallback."""
    if not _HAS_COLOR:
        return text
    code = PINK if _is_256color() else BRIGHT_MAGENTA
    return _c(text, code)


# ── Boot animation ──────────────────────────────────────────────────────

_enable_ansi()

CAT = r"""      /\_/\
     ( o.o )
      > ^ <  """


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
    """Return layer lines with each layer name colored by its fixed layer color."""
    result: list[str] = []
    for raw_line in LAYERS.split("\n"):
        colored_parts: list[str] = []
        for token in raw_line.split():
            # Map token (e.g. "gateway_01") to its base layer name
            base = token.split("_")[0] if "_" in token else token
            if base in LAYER_COLORS:
                colored_parts.append(c_layer(token, base))
            else:
                colored_parts.append(token)
        colored_line = " ".join(colored_parts)
        result.append("\u2551" + colored_line.center(W) + "\u2551")
    return result


def print_header() -> None:
    print(_pink(CAT))
    print(_pink(BANNER))
    for line in _layer_lines():
        print(_pink(line))
    print(_pink(BANNER_BOTTOM))


# ── Public helpers ──────────────────────────────────────────────────────


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


def print_step_header(step_num: int, total: int, tool_name: str) -> None:
    """Print step header with runner-layer colored step number and tool name."""
    c_runner = layer_color("runner")
    c2 = _pick()
    sep = "--" if os.name == "nt" else "\u2500\u2500"
    s = f"\n  {_c(sep, c_runner)} {_c(f'Step {step_num}/{total}', c_runner)} {_c(sep * 20, c_runner)}"
    s += f"\n  {_c('Tool:', c2)}    {_c(tool_name, c2)}"
    s += f"\n  {_c('Status:', 33)}  {_c('Running...', 33)}"
    print(s)


def print_step_result(success: bool, duration_s: float, tokens: int = 0) -> None:
    """Update step completion line with green/red status."""
    if success:
        status = _c("[ok]", 92)
    else:
        status = _c("[!!]", 91)
    token_str = ", " + _c(f"{tokens} tokens", 96) if tokens else ""
    duration_str = _c(f"{duration_s:.1f}s", 93)
    print(f"\r  Status:  {status}  ({duration_str}{token_str})")


def print_session_summary(
    run_id: str,
    steps: int,
    duration_ms: float,
    token_usage: dict[str, int],
    tool_summary: dict[str, int],
) -> None:
    """Print a colored session summary box using harness-layer colors."""
    c = layer_color("harness")
    line = _c("=" * W, c)
    print(f"\n{line}")
    print(f"  {_c('Run ID:', c)}    {run_id}")
    print(f"  {_c('Steps:', c)}     {steps}")
    print(f"  {_c('Duration:', c)}  {duration_ms:.0f}ms")
    if token_usage.get("total_tokens", 0) > 0:
        tu = token_usage
        t_total = f"{tu['total_tokens']:,}"
        t_prompt = f"{tu['prompt_tokens']:,}"
        t_comp = f"{tu['completion_tokens']:,}"
        print(f"  {_c('Tokens:', c)}    {_c(t_total, 93)} "
              f"(prompt: {_c(t_prompt, 94)} "
              f"+ completion: {_c(t_comp, 94)})")
    if tool_summary:
        print()
        for tool_name, count in sorted(tool_summary.items()):
            plural = "call" if count == 1 else "calls"
            print(f"    {_c(tool_name, _pick()):<20} {_c(str(count), _pick())} {plural}")
    print(line)
