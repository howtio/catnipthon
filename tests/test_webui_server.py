from __future__ import annotations

from src.shared.webui_server import _coerce_history, _extract_result


def test_extract_result_from_final_report() -> None:
    report = "\n".join(
        [
            "Run ID: abc123",
            "Steps: 3",
            "",
            "## Result",
            "第一行回答",
            "第二行回答",
            "",
            "## Modified Files",
            "- src/main.py",
        ],
    )

    result = _extract_result(report)

    assert result == "第一行回答\n第二行回答"


def test_extract_result_without_marker_returns_original_text() -> None:
    assert _extract_result("plain answer") == "plain answer"


def test_coerce_history_builds_runner_message_format() -> None:
    history = _coerce_history(
        [
            {"question": "你好", "answer": "你好呀"},
            {"question": "继续", "answer": ""},
            "ignored",
        ],
    )

    assert history == [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好呀"},
        {"role": "user", "content": "继续"},
    ]
