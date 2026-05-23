# 11 Executor — 执行层

## 一句话职责

监听工具调用事件，执行 guard 检查，执行真实工具，发布结果。

## 关键原则

```
Executor 是唯一副作用边界。
所有文件读写、patch、shell 执行，只能发生在 Executor。
```

## 文件结构

```
executor_11/
  __init__.py           — 导出 wrapper 和 types
  wrapper.py            — 本层唯一对外入口
  types.py              — 本层类型定义
  execute_tool.py       — 工具执行入口
  execute_resolved_tool.py — 已解析工具执行
  audit_tool_call.py    — 审计日志
  handle_tool_error.py  — 工具错误处理
  guard.py              — Guard 统一入口
  tools.py              — 工具实现
  policy/
    permission_guard.py — 权限检查
    path_guard.py       — 路径边界检查
    command_guard.py    — 命令白名单检查
```

## 三层 Guard

| Guard | 职责 |
|-------|------|
| permissionGuard | 检查工具所需权限等级 (low/medium/high) |
| pathGuard | 限制文件操作不超出 workspace 边界 |
| commandGuard | shell 命令白名单，阻止危险命令 (rm/sudo/curl/ssh...) |

## 依赖

- 09-eventbus
- 10-tool-registry
- subprocess + pathlib

## 允许

- 文件读写
- shell 执行（受 commandGuard 约束）
- 浏览器打开（受 pathGuard 约束）

## 禁止

- 不做推理
- 不做任务规划
