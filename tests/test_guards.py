from __future__ import annotations

from src.layers.executor_11.policy.permission_guard import check_permission, PermissionDenied
from src.layers.executor_11.policy.path_guard import check_path, PathForbidden
from src.layers.executor_11.policy.command_guard import check_command, CommandForbidden
from src.layers.executor_11.guard import run_guards
from src.layers.tool_registry_10 import ToolRegistryLayerApi


def test_permission_low_granted() -> None:
    check_permission("list_files", "low", "low")  # should not raise


def test_permission_insufficient() -> None:
    try:
        check_permission("shell_exec", "high", "low")
        assert False, "should have raised"
    except PermissionDenied:
        pass


def test_path_within_workspace() -> None:
    resolved = check_path(".")
    assert resolved is not None


def test_path_outside_workspace() -> None:
    try:
        check_path("..\\..\\..\\..\\etc\\passwd")
        assert False, "should have raised"
    except PathForbidden:
        pass


def test_command_whitelisted() -> None:
    result = check_command("python --version")
    assert result == "python --version"


def test_command_blocked() -> None:
    try:
        check_command("sudo rm -rf /")
        assert False, "should have raised"
    except CommandForbidden:
        pass


def test_command_empty() -> None:
    try:
        check_command("")
        assert False, "should have raised"
    except CommandForbidden:
        pass


def test_guard_integration() -> None:
    registry = ToolRegistryLayerApi()
    args = run_guards("list_files", {"path": "."}, registry)
    assert args["path"] is not None


def test_guard_unknown_tool() -> None:
    registry = ToolRegistryLayerApi()
    try:
        run_guards("nonexistent", {}, registry)
        assert False, "should have raised"
    except Exception:
        pass


def test_url_guard_allows_public_url() -> None:
    registry = ToolRegistryLayerApi()
    args = run_guards("web_fetch", {"url": "https://example.com"}, registry)
    assert args["url"] == "https://example.com"


def test_url_guard_blocks_localhost() -> None:
    registry = ToolRegistryLayerApi()
    try:
        run_guards("web_fetch", {"url": "http://localhost:8080/secret"}, registry)
        assert False, "should have raised"
    except Exception:
        pass


def test_url_guard_blocks_internal_ip() -> None:
    registry = ToolRegistryLayerApi()
    try:
        run_guards("web_fetch", {"url": "http://192.168.1.1/admin"}, registry)
        assert False, "should have raised"
    except Exception:
        pass
