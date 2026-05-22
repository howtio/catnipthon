# Layer Status：11 层实现状态一览

> 某一层有开发动作时，只需更新对应段落。
> 本文件替代原来的 11 个独立分层进度日志。

---

## 01 Gateway

**状态**: 已实现（Phase 1）

**已实现:**
- CLI 参数解析（sys.argv）
- RunTask 创建（id + user_message）
- 异步提交到 Queue（enqueue + wait_for_completion）
- 结果展示（终端输出 done/failed）

---

## 02 Queue

**状态**: 已实现（Phase 1）

**已实现:**
- 内存 FIFO 队列（asyncio.Queue）
- 入队/出队（enqueue/dequeue）
- 任务状态管理（pending → running → done / failed）
- 任务快照和完成等待（get_task_snapshot / wait_for_completion）

---

## 03 Worker

**状态**: 已实现（Phase 1）

**已实现:**
- Worker 异步消费循环（start/stop）
- 调用 Harness 处理任务（_process）
- 错误处理与捕获（try/except → failed）
- 待实现: 并发控制、Worker 心跳

---

## 04 Harness

**状态**: 已实现（Phase 2）

**已实现:**
- runId 创建与生命周期管理
- 调用链串联（Context → Skills → Memory → Runner）
- final report 生成（steps/tool calls/answer/context summary）
- EventBus 事件发布（run.started/prompt.composed/run.finished）

**待实现:**
- 验收检查
- safe_git_diff
- 步数限制策略
- run 级超时控制

---

## 05 Context

**状态**: 已实现（Phase 2）

**已实现:**
- 关键文档加载（ONBOARD.md / CLAUDE.md / CODEX_ARCHITECTURE.md / CODEX_MASTER_REQUIREMENTS.md）
- workspace 扫描与文件树摘要
- system prompt 构建（Project Context + Workspace State + Current Task）
- 开工清单提取（从 ONBOARD.md 解析）

---

## 06 Skills

**状态**: 已实现（Phase 2）

**已实现:**
- 技能注册表（5 个技能：coding/testing/debugging/refactor/review）
- 关键词匹配选择（每技能 5-9 个关键词）
- SKILL.md 文件加载（skills/<name>/SKILL.md）
- 技能说明注入（prompt 格式化）
- 无匹配时默认 fallback 到 coding

---

## 07 Memory

**状态**: 已实现（Phase 2）

**已实现:**
- MemorySnapshot 数据结构（session_entries / working_set / observations / project_recent / carryover / checklist）
- WorkingSet 工作对象追踪（focused_file / recent_files / openable_html）
- JSON 持久化（logs/catnip-memory.json）
- 记忆裁剪（session 50 条 / observations 20 条 / recent files 10 条）
- 记忆注入 prompt 生成

---

## 08 Runner

**状态**: 占位实现（Phase 2）

**已实现:**
- RunnerResult 数据结构（answer / steps_used / tool_calls_made）
- Phase 2 占位（返回 mock answer + 上下文长度）

**待实现:**
- ReAct Loop
- Provider 抽象（heuristic + DeepSeek）
- AI SDK 集成
- 步数限制与重试

---

## 09 EventBus

**状态**: 已实现（Phase 2）

**已实现:**
- 异步事件发布订阅（publish/subscribe/unsubscribe）
- 事件类型常量（13 种：run.*/agent.*/tool.*/worker.*/prompt.*）

**待实现:**
- 工具调用事件传递（tool.call.requested → result 路由）
- waitForToolResult
- Logger 旁路订阅

---

## 10 Tool Registry

**状态**: 未开始（仅 README）

**待实现:**
- 工具定义注册
- 工具 schema 声明
- 工具解析接口
- 权限等级声明

---

## 11 Executor

**状态**: 未开始（仅 README）

**待实现:**
- 工具调用监听
- permissionGuard
- pathGuard
- commandGuard
- 工具执行
- 审计日志

---

## Shared

**状态**: 已实现（Phase 1）

**已实现:**
- types: RunTask、TaskStatus
- logger: get_logger（控制台日志、可扩展 handler）
- errors: CatnipError、QueueError、WorkerError、GatewayError、HarnessError
- utils: createId

**待实现:**
- types: permission、tool、event、result
- errors: PolicyError、ToolError、TimeoutError
- utils: sleep、safeJson、assertNever
