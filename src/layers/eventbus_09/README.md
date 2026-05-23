# 09 EventBus — 事件层

## 一句话职责

传递所有 run / step / tool / heartbeat 事件，让 Logger 旁路订阅。

## 文件结构

```
eventbus_09/
  __init__.py          — 导出 wrapper 和 types
  wrapper.py           — 本层唯一对外入口
  types.py             — 本层类型定义
  event_bus.py         — 事件系统实现
  publish_event.py     — 事件发布
  subscribe_event.py   — 事件订阅
  wait_for_tool_result.py — 工具结果等待
  tool_call_router.py  — 工具调用路由
  event_types.py       — 事件类型常量
```

## 核心事件

```
run.started
run.finished
run.heartbeat
agent.step.finished
agent.plan.generated
agent.reasoning.summary
agent.answer.produced
tool.call.requested
tool.call.result
tool.call.failed
worker.heartbeat
prompt.composed
```

## 依赖

- 无（Python asyncio.Event 或自定义事件系统）

## 允许

- 事件发布订阅
- 事件过滤和等待

## 禁止

- MVP 不引入 Redis / Kafka / MQ
