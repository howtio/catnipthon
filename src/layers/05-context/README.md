# 05 Context — 上下文层

## 一句话职责

读取施工文档、扫描 workspace、加载历史、构建 system prompt。

## 文件结构

```
05-context/
  __init__.py                — 导出 wrapper 和 types
  wrapper.py                 — 本层唯一对外入口
  types.py                   — 本层类型定义
  build_context.py           — 上下文构建
  load_docs.py               — 文档加载
  scan_workspace.py          — workspace 扫描
  load_session_history.py    — 历史加载
  summarize_workspace.py     — workspace 摘要
  build_base_system_prompt.py — system prompt 构建
```

## 依赖

- 文件系统（只读）

## 允许

- 读取 docs/ 目录
- 扫描 workspace 文件树
- 提取开工清单和待续任务

## 禁止

- 不修改 workspace
- 不执行 shell
- 不调用模型
