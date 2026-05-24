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
    )
    return report


def format_final_report(report: FinalReport) -> str:
    """Format a final report as a human-readable string."""
    lines = [
        f"Run ID: {report.run_id}",
        f"Steps: {report.steps_used}",
        f"Duration: {report.duration_ms:.0f}ms",
        f"",
        f"## Result",
        f"{report.final_answer}",
    ]
    if report.modified_files:
        lines.extend(["", "## Modified Files"])
        for f in report.modified_files:
            lines.append(f"- {f}")
    return "\n".join(lines)
