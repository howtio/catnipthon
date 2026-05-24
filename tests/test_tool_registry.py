from __future__ import annotations

from src.layers.tool_registry_10 import ToolRegistryLayerApi


def test_registry_has_six_tools() -> None:
    registry = ToolRegistryLayerApi()
    tools = registry.list_tools()
    assert len(tools) == 6


def test_registry_get_tool_by_name() -> None:
    registry = ToolRegistryLayerApi()
    tool = registry.get_tool("read_file")
    assert tool is not None
    assert tool.name == "read_file"
    assert tool.category == "fs"


def test_registry_has_tool() -> None:
    registry = ToolRegistryLayerApi()
    assert registry.has_tool("shell_exec") is True
    assert registry.has_tool("nonexistent") is False


def test_registry_category_filter() -> None:
    registry = ToolRegistryLayerApi()
    fs_tools = registry.list_tools("fs")
    assert len(fs_tools) >= 3  # list_files, read_file, write_file, patch_file


def test_registry_to_openai_schemas() -> None:
    registry = ToolRegistryLayerApi()
    schemas = registry.to_openai_schemas()
    assert len(schemas) == 6
    assert schemas[0]["type"] == "function"
