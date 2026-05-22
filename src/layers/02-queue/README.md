# 02 Queue — 队列层

## 一句话职责

任务入队、出队、状态管理。MVP 使用内存 FIFO 队列。

## 文件结构

```
02-queue/
  __init__.py          — 导出 wrapper 和 types
  wrapper.py           — 本层唯一对外入口
  types.py             — 本层类型定义
  in_memory_queue.py   — 内存 FIFO 队列实现
  enqueue_task.py      — 入队逻辑
  dequeue_task.py      — 出队逻辑
  task_status_store.py — 任务状态存储
```

## 依赖

- 无

## 允许

- 内存 FIFO 队列
- 任务状态 pending / running / done / failed
- 任务快照和完成等待
- 队列订阅通知

## 禁止

- 不消费任务（归属 Worker）
- 不管理线程池（归属 Worker）
- 不调用 Harness
- 不理解任务语义
