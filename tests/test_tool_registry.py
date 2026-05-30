from __future__ import annotations

from src.layers.tool_registry_10 import ToolRegistryLayerApi


def test_registry_has_ten_tools() -> None:
    registry = ToolRegistryLayerApi()
    tools = registry.list_tools()
    assert len(tools) == 10  # 6 MVP + 4 v4.0 (web_fetch, web_search, open_browser, file_search)


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
    assert len(fs_tools) >= 4  # list_files, read_file, write_file, patch_file, file_search
    web_tools = registry.list_tools("web")
    assert len(web_tools) == 3  # web_fetch, web_search, open_browser


def test_registry_to_openai_schemas() -> None:
    registry = ToolRegistryLayerApi()
    schemas = registry.to_openai_schemas()
    assert len(schemas) == 10
    assert schemas[0]["type"] == "function"
