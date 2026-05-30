"""catnip-agent — Claude Code-style CLI: batch mode + interactive REPL."""

from __future__ import annotations

import os
import sys
import time

from src.shared.cli import H_LINE, print_header, print_divider, print_summary_claude
from src.shared.interactive import run_interactive
from src.shared.webui_server import run_webui_server
from src.bootstrap import bootstrap


def main() -> None:
    app = bootstrap()
    print_header()

    if len(sys.argv) > 1 and sys.argv[1] == "--webui":
        run_webui_server(app)
        return

    if len(sys.argv) > 1:
        # Batch mode: run a single task
        user_msg = " ".join(sys.argv[1:])
        provider = os.environ.get("CATNIP_RUNNER_PROVIDER", "deepseek")
        print(f"  Task: {user_msg[:60]}{'...' if len(user_msg) > 60 else ''}")
        print(f"  Mode: batch  |  Provider: {provider}")
        print_divider()

        start = time.time()
        try:
            result = app.gateway.run_cli(sys.argv[1:])
        except Exception as e:
            print(f"  [!] Error: {e}")
            sys.exit(1)

        duration_ms = (time.time() - start) * 1000

        # Collect metrics from eventbus
        step_events = app.eventbus.get_history("agent.step.finished")
        tool_events = app.eventbus.get_history("tool.call.requested")
        llm_events = app.eventbus.get_history("llm.usage")
        steps_used = len(step_events)
        token_usage = {
            "prompt_tokens": sum(e.payload.get("prompt_tokens", 0) for e in llm_events),
            "completion_tokens": sum(e.payload.get("completion_tokens", 0) for e in llm_events),
            "total_tokens": sum(e.payload.get("total_tokens", 0) for e in llm_events),
        }
        tool_summary: dict[str, int] = {}
        for te in tool_events:
            tn = te.payload.get("tool_name", "")
            if tn:
                tool_summary[tn] = tool_summary.get(tn, 0) + 1

        print_summary_claude(
            steps=steps_used or 1,
            duration_ms=duration_ms,
            token_usage=token_usage,
            tool_counts=tool_summary,
        )

        print_divider()
        try:
            print(result.strip())
        except UnicodeEncodeError:
            safe = result.strip().encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
                sys.stdout.encoding or "utf-8", errors="replace"
            )
            print(safe)
        print_divider()
    else:
        # Interactive mode
        run_interactive(app)


if __name__ == "__main__":
    main()
