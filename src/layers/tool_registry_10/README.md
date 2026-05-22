# 10 Tool Registry — 工具注册层

## 一句话职责

注册工具定义，管理工具元数据，为 AI SDK 和 Executor 提供工具信息。

## 关键原则

```
Tool Registry 只说明"工具是什么"。
Executor 才负责"工具怎么执行"。
```

## 文件结构

```
10-tool-registry/
  __init__.py           — 导出 wrapper 和 types
  wrapper.py            — 本层唯一对外入口
  types.py              — 本层类型定义
  tool_registry.py      — 注册表实现
  register_tools.py     — 工具注册
  resolve_tool.py       — 工具解析
  validate_tool_schema.py — schema 校验
  list_available_tools.py — 工具列表
  tools/
    list_files.definition.py
    read_file.definition.py
    write_file.definition.py
    patch_file.definition.py
    shell_exec.definition.py
    git_diff.definition.py
```

## 工具分类

| Category | 工具 |
|----------|------|
| fs | list_files, read_file, write_file, patch_file |
| shell | shell_exec |
| vcs | git_diff |
| browser | open_browser, open_url |
| web | web_search, open_browser_search |

## 依赖

- 无

## 允许

- 管理工具元数据
- 按 category 筛选工具

## 禁止

- 不直接读写文件
- 不执行 shell
- 不绕过 Executor
