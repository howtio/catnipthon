"""Catnip CLI rendering — Claude Code-style clean output.

Import `print_header`, `print_step_claude`, `print_result_claude`,
`print_summary_claude`, `print_thinking` from here.
"""

from __future__ import annotations

import os
import sys

from src.shared.version import VERSION_TAG

W = 46
H_LINE = "\u2500" * W
EQUAL_LINE = "=" * W

TITLE = "catnip agent"
SUBTITLE = "11-Layer Coding Agent Runtime"

LAYERS = (
    "gateway_01 -> queue_02 -> worker_03\n"
    "harness_04 -> context_05 -> skills_06\n"
    "memory_07 -> runner_08 -> eventbus_09\n"
    "tool_registry_10 -> executor_11"
)

# ── ANSI color support ──────────────────────────────────────────────────

_RESET = "\033[0m"
_HAS_COLOR = sys.stdout.isatty() and os.environ.get("TERM") != "dumb"

# Fixed professional palette (Claude Code style)
INFO = 37     # white
OK = 32       # green
WARN = 33     # yellow
ERROR = 91    # red
HIGHLIGHT = 96  # cyan (tool names, highlights)
DIM = 90      # gray (secondary info)


def _enable_ansi() -> None:
    """Enable ANSI on Windows 10+ consoles."""
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def _c(text: str, color_code: int) -> str:
    """Wrap text in ANSI color if terminal supports it."""
    if not _HAS_COLOR:
        return text
    return f"\033[{color_code}m{text}{_RESET}"


def _strip_ansi(text: str) -> str:
    """Remove ANSI codes for width calculation."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)


# ── Symbol constants (Claude Code style) ───────────────────────────────

SYM_SUB = "\u25c7"     # ◇
SYM_BRANCH = "\u2503"  # ┃
SYM_OK = "\u2713"      # ✓
SYM_FAIL = "\u2717"    # ✗


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


BANNER = f"""{'=' * W}
{_pad_center(TITLE + '  ' + VERSION_TAG)}
{_pad_center(SUBTITLE)}
{'=' * W}"""


def print_header() -> None:
    """Print pink boot animation with cat and version."""
    print()
    print(_pink(CAT))
    print(_pink(BANNER))
    for line in LAYERS.split("\n"):
        print(_pink("  " + line.center(W - 2)))
    print()


# ── Divider ─────────────────────────────────────────────────────────────


def print_divider(title: str = "") -> None:
    """Print a thin divider line with optional centered title."""
    if title:
        side_len = (W - len(title) - 2) // 2
        line = f"{'─' * side_len} {title} {'─' * side_len}"
        if len(line) < W:
            line = "─" * W
    else:
        line = "─" * W
    print(f"  {_c(line, DIM)}")


# ── Claude Code-style output functions ──────────────────────────────────


def print_step_claude(step_num: int, tool_name: str, args_summary: str = "") -> None:
    """Print a Claude Code-style step header.

    Format:
      ◇ Tool: read_file
        ┃ path: src/main.py
    """
    print(f"\n  {SYM_SUB} {_c('Tool:', DIM)} {_c(tool_name, HIGHLIGHT)}")
    if args_summary:
        print(f"  {SYM_BRANCH} {_c(args_summary, DIM)}")


def print_result_claude(success: bool, duration_s: float, tokens: int = 0) -> None:
    """Print step completion result (overwrites status line).

    Format:  ◇ ✓ (1.2s · 450t)
             ◇ ✗ Error details
    """
    token_str = f" \u00b7 {tokens}t" if tokens else ""
    if success:
        status = _c(f"{SYM_OK} ({duration_s:.1f}s{token_str})", OK)
    else:
        status = _c(f"{SYM_FAIL} ({duration_s:.1f}s{token_str})", ERROR)
    print(f"\r  {SYM_SUB} {status}")


def print_summary_claude(
    steps: int,
    duration_ms: float,
    token_usage: dict[str, int],
    tool_counts: dict[str, int],
) -> None:
    """Print a Claude Code-style session summary.

    Format:
      ──────────────── Summary ────────────────
      ◇ 3 steps · 5.2s · 1,340 tokens
      ◇ Tools: read_file (2), list_files (1)
    """
    print()
    print_divider("Summary")
    duration_s = duration_ms / 1000
    total_tokens = token_usage.get("total_tokens", 0)
    parts = [f"{steps} step{'s' if steps != 1 else ''}",
             f"{duration_s:.1f}s"]
    if total_tokens:
        parts.append(f"{total_tokens:,} tokens")
    print(f"  {SYM_SUB} {' \u00b7 '.join(parts)}")
    if tool_counts:
        tool_list = ", ".join(f"{name} ({count})" for name, count in sorted(tool_counts.items()))
        print(f"  {SYM_SUB} {_c('Tools:', DIM)} {tool_list}")


def print_thinking(text: str, elapsed_s: float = 0, heartbeat: bool = False) -> None:
    """Print Claude Code-style thinking/reasoning text with elapsed time.

    Regular reasoning:  > thinking text here...
    Heartbeat ping:     > thinking... (5.2s)
    """
    if heartbeat:
        print(f"\r  {_c(f'> thinking... ({elapsed_s:.0f}s)', DIM)}", end="")
        return
    if not text:
        return
    time_str = f" ({elapsed_s:.1f}s)" if elapsed_s else ""
    line = text[:80].replace("\n", " ")
    print(f"\r  {_c(f'> {line}{time_str}', DIM)}")


def print_user_message(msg: str) -> None:
    """Print user message in Claude Code style with '>' prompt prefix."""
    print(f"\n  > {msg}")
    print_divider()
