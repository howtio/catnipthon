"""Tests for v4.0 tools: web_fetch, web_search, open_browser, file_search."""

from __future__ import annotations

from unittest.mock import patch

from src.layers.executor_11.tools import open_browser, file_search


def test_open_browser_http() -> None:
    with patch("webbrowser.open", return_value=True) as mock_open:
        result = open_browser("https://example.com")
        assert "Opened browser" in result
        mock_open.assert_called_once_with("https://example.com")


def test_open_browser_rejects_non_http() -> None:
    result = open_browser("file:///etc/passwd")
    assert "Error" in result


def test_file_search_by_glob_py() -> None:
    """Should find at least some .py files in the workspace."""
    result = file_search("*.py", max_results=5)
    assert result
    assert "Error" not in result
    assert ".py" in result


def test_file_search_by_content() -> None:
    """Search for content known to exist in the codebase."""
    result = file_search("*.py", content="def ", max_results=5)
    assert result
    assert "Error" not in result


def test_file_search_no_match() -> None:
    result = file_search("zzz_nonexistent_file_xyzzy.py")
    assert "no matches" in result


def test_file_search_validates_max() -> None:
    result = file_search("*.py", max_results=999)
    assert result
    assert "Error" not in result
