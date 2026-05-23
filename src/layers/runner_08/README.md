# 08 Runner — 决策层

## 一句话职责

调用 AI SDK 执行受控 ReAct Loop，决策工具调用，产出最终回答。

## 关键约束

```
Runner 不直接执行工具。
Runner 只能通过 EventBus 发起 tool.call.requested。
Runner 不直接读写文件，不直接执行 shell。
```

## 文件结构

```
runner_08/
  __init__.py            — 导出 wrapper 和 types
  wrapper.py             — 本层唯一对外入口
  types.py               — 本层类型定义
  agent_runner.py        — Agent 运行器
  build_ai_tools.py      — OpenAI tool schemas 构建
  run_openai_chat.py     — OpenAI chat completions 调用
  handle_step_finish.py  — step 完成处理
  normalize_result.py    — 结果归一化
  provider.py            — Provider 实现（heuristic / deepseek）
  planner.py             — 工具计划生成
```

## 依赖

- 09-eventbus
- openai Python SDK（DeepSeek OpenAI 兼容接口）

## 允许

- 调用 OpenAI-compatible chat completions API（tool calling）
- 管理 step 计数和工具重试
- Provider 选择

## 禁止

- 不直接执行工具
- 不直接维护 session memory（委托给 Memory 层）
- 不绕过 Memory 自行缓存历史
