# Layer Status：11 层实现状态一览

> 某一层有开发动作时，只需更新对应段落。

---

## 01 Gateway

**状态**: Phase 1 — 已实现（基于 argparse 的最小 CLI 管道）

**已实现:**
- parse_cli_args: argparse 参数解析
- validate_user_input: 非空校验
- create_run_task: UUID + RunTask 创建
- wrapper: GatewayLayerApi 公开接口（run_cli）

**待实现:**
- 交互模式 readline
- 结果格式化增强

## 02 Queue

**状态**: Phase 1 — 已实现（内存 FIFO 队列 + 状态管理）

**已实现:**
- in_memory_queue: deque 实现 FIFO
- task_status_store: dict 映射 task_id → RunTask
- enqueue_task/dequeue_task: 入队/出队
- wrapper: QueueLayerApi 公开接口（enqueue/dequeue/get_task/update_status）

**待实现:**
- 队列订阅通知
- 任务快照和完成等待

## 03 Worker

**状态**: Phase 1 — 已实现（同步消费循环 + 可注入处理函数）

**已实现:**
- run_worker_loop: 同步消费循环（poll → dequeue → process）
- process_run_task: 单任务处理（注入 callable 或 echo 占位）
- mark_task_status: done/failed 标记
- handle_worker_error: 错误捕获
- wrapper: WorkerLayerApi 公开接口

**待实现:**
- 线程池/并发消费槽
- Worker 心跳生成

## 04 Harness

**状态**: Phase 2 — 已实现（Run 生命周期 + Context→Skills→Memory→Runner 串联）

**已实现:**
- create_run: UUID + RunInfo 创建
- run_lifecycle: 顺序调用 Context→Skills→Memory→Runner（mock）
- build_final_report: FinalReport 构建 + 格式化
- wrapper: HarnessLayerApi 公开接口

**待实现:**
- max_step_policy
- acceptance_check
- safe_git_diff

## 05 Context

**状态**: Phase 2 — 已实现（文档加载 + Workspace 扫描 + System Prompt）

**已实现:**
- load_docs: 读取 docs/*.md 文档
- scan_workspace: 递归扫描工作区（排除 .venv/__pycache__/.git 等）
- build_base_system_prompt: 组装 system prompt（文档 + 树 + 清单）
- build_context: 上下文构建入口
- wrapper: ContextLayerApi 公开接口

## 06 Skills

**状态**: Phase 2 — 已实现（技能注册 + 关键词匹配 + SKILL.md 加载注入）

**已实现:**
- skill_registry: 5 个技能注册（coding/testing/debugging/refactor/review）
- skill_matcher: 关键词匹配
- select_skills: 技能选择 + fallback 到 coding
- load_skill_markdown: 加载 skills/*/SKILL.md
- inject_skills: 注入到 system prompt
- wrapper: SkillsLayerApi 公开接口

## 07 Memory

**状态**: Phase 2 — 已实现（MemorySnapshot + JSON 持久化）

**已实现:**
- MemorySnapshot: sessionEntries / workingSet / observations / carryoverTasks
- WorkingSet: focusedFilePath / recentFilePaths
- JSON 持久化到 logs/catnip-memory.json
- build_memory_block: 格式化记忆块注入
- wrapper: MemoryLayerApi 公开接口

**待实现:**
- 记忆裁剪策略增强
- 从工具结果抽取工作对象

## 08 Runner

**状态**: Phase 2 占位符（Phase 3 实现真实 ReAct loop）

## 09 EventBus

**状态**: Phase 2 — 已实现（内存 pub/sub 事件系统）

**已实现:**
- event_bus: 内存事件总线（publish/subscribe/unsubscribe）
- event_types: 11 个事件类型常量（run.* / agent.* / tool.call.* / worker.* / prompt.*）
- publish_event / subscribe_event 便捷封装
- wrapper: EventBusLayerApi 公开接口

**待实现:**
- waitForToolResult
- tool_call_router

## 10 Tool Registry

**状态**: 未开始（仅 README + __init__）

## 11 Executor

**状态**: 未开始（仅 README + __init__）

## Shared

**状态**: 已实现（脚手架 3.0）

**已实现:**
- types: RunTask、TaskStatus
- errors: CatnipError、QueueError、WorkerError、GatewayError、HarnessError
- logger: get_logger（控制台日志）
- utils: create_id
- version: 版本号从 pyproject.toml 单一真相源读取
- cli: catnip 品牌 CLI 开机动画（TITLE/SUBTITLE/LAYERS 可覆盖）
