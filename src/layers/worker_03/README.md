# 03 Worker — 消费层

## 一句话职责

从 Queue 消费任务，控制并发，调用 Harness，维护心跳。

## 文件结构

```
worker_03/
  __init__.py           — 导出 wrapper 和 types
  wrapper.py            — 本层唯一对外入口
  types.py              — 本层类型定义
  run_worker_loop.py    — Worker 循环
  process_run_task.py   — 任务处理
  mark_task_status.py   — 状态标记
  handle_worker_error.py — 错误处理
```

## 依赖

- 02-queue
- 04-harness

## 允许

- 线程池 / 并发消费槽
- Worker 心跳生成
- 错误捕获与分类

## 禁止

- 不构建 prompt
- 不直接调用模型
- 不直接执行工具
