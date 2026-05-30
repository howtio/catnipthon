from __future__ import annotations

from src.layers.harness_04.types import RunInfo, FinalReport


def build_final_report(run: RunInfo) -> FinalReport:
    """Build a final report from run info."""
    report = FinalReport(
        run_id=run.run_id,
        steps_used=run.steps_used,
        duration_ms=run.duration_ms,
        final_answer=run.final_answer,
        tool_summary=dict(run.tool_summary),
        modified_files=list(run.modified_files),
        risks=[],
        rollback_guide="",
        token_usage=dict(run.token_usage),
    )
    return report


def format_final_report(report: FinalReport) -> str:
    """Format a final report as a human-readable string."""
    lines = [
        f"Run ID: {report.run_id}",
        f"Steps: {report.steps_used}",
        f"Duration: {report.duration_ms:.0f}ms",
    ]
    if report.token_usage.get("total_tokens", 0) > 0:
        lines.append(f"Tokens: {report.token_usage['total_tokens']:,}")
        lines.append(f"  Prompt: {report.token_usage['prompt_tokens']:,}")
        lines.append(f"  Completion: {report.token_usage['completion_tokens']:,}")
    if report.tool_summary:
        tools_str = ", ".join(f"{k} ({v})" for k, v in report.tool_summary.items())
        lines.append(f"Tools used: {tools_str}")
    lines.extend(["", "## Result", f"{report.final_answer}"])
    if report.modified_files:
        lines.extend(["", "## Modified Files"])
        for f in report.modified_files:
            lines.append(f"- {f}")
    return "\n".join(lines)
