# Layer Status：11 层实现状态一览

> 某一层有开发动作时，只需更新对应段落。

---

## 01 Gateway

**状态**: CLI 2.0 — 已实现（基于 argparse 的 CLI 管道 + 交互式 REPL）

**已实现:**
- parse_cli_args: argparse 参数解析
- validate_user_input: 非空校验
- create_run_task: UUID + RunTask 创建
- wrapper: GatewayLayerApi 公开接口（run_cli）
- 交互式 REPL（src/shared/interactive.py）
- 实时进度跟踪（ProgressTracker 通过 EventBus 订阅显示 tool 调用/步骤完成）
- 提供商运行时切换（/provider heuristic|deepseek）
- 内部命令（/help /exit /clear /history）
- `src/main.py --webui` Web UI 启动入口（进行中）
- Web UI 当前已具备暂停前可交接入口，后续重点是低高度布局与使用流畅度收口

## 02 Queue

**状态**: v3.0 — 已实现（内存 FIFO 队列 + 阻塞等待 + 心跳 + 追加要求）

**已实现:**
- in_memory_queue: deque 实现 FIFO + threading.Event 阻塞等待（wait_for_task）
- task_status_store: dict 映射 task_id → RunTask（含 append_requirement / update_heartbeat / get_stale_tasks / get_running）
- enqueue_task/dequeue_task: 入队/出队
- wrapper: QueueLayerApi 公开接口（enqueue/dequeue/wait_for_task/append_requirement/update_heartbeat/get_stale_tasks/get_running_tasks）

## 03 Worker

**状态**: v3.0 — 已实现（阻塞等待 + 错误处理 + 后台心跳）

**已实现:**
- run_worker_loop: 同步消费循环（wait_for_task 阻塞等待 + try/except 错误处理）
- wrapper: WorkerLayerApi 公开接口（含 run_with_heartbeat 后台心跳守护线程）

## 04 Harness

**状态**: Phase 7 — 已实现（完整 run 生命周期 + 指标收集 + JSONL 日志）

**已实现:**
- create_run: UUID + RunInfo 创建
- run_lifecycle: 顺序调用 Context→Skills→Memory→Runner（含真实 agent loop）
- run_lifecycle: 自动收集 tool_summary、step count、modified_files
- build_final_report: FinalReport 构建 + 格式化（含工具计数、修改文件列表）
- wrapper: HarnessLayerApi 公开接口（注入所有依赖）

**待实现:**
- max_step_policy
- acceptance_check
- safe_git_diff
- Web UI 真实联调验证（进行中）

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

**状态**: v4.0 — 已实现（MemorySnapshot + JSON 持久化 + SessionMemory）

**已实现:**
- MemorySnapshot: sessionEntries / workingSet / observations / carryoverTasks
- WorkingSet: focusedFilePath / recentFilePaths
- JSON 持久化到 logs/catnip-memory.json
- build_memory_block: 格式化记忆块注入
- SessionMemory: 进程内会话跟踪（files_read, files_written, tool_counts, user_notes, turn_summaries）
- build_context: 构建紧凑会话上下文注入 system prompt
- wrapper: MemoryLayerApi 公开接口

**待实现:**
- 记忆裁剪策略增强
- 从工具结果抽取工作对象

## 08 Runner

**状态**: v4.0 — 已实现（DeepSeek chat + token 优化 + 追加要求注入）

**已实现:**
- provider: heuristic_plan（关键词规则路由）
- deepseek_provider: 基于 OpenAI SDK 的 DeepSeek API 调用（deepseek-chat + 系统消息原生支持 + 历史压缩 + 结果截断 + 追加要求注入）
- agent_runner: agent loop（计划 → 工具请求 → 等待结果 → 步骤完成 → 最终回答）
- wrapper: RunnerLayerApi 公开接口（run + config + system_prompt + conversation_history）

## 09 EventBus

**状态**: Phase 3 — 已实现（内存 pub/sub + waitForToolResult）

**已实现:**
- event_bus: 内存事件总线（publish/subscribe/unsubscribe）
- event_types: 17 个事件类型常量（含 QUEUE_HEARTBEAT、AGENT_REASONING_CHUNK、AGENT_ASKING_USER、AGENT_USER_RESPONSE）
- publish_event / subscribe_event 便捷封装
- waitForToolResult: threading.Event 实现工具结果等待
- wrapper: EventBusLayerApi 公开接口（含 waitForToolResult）

**待实现:**
- tool_call_router（Phase 4+）

## 10 Tool Registry

**状态**: v4.0 — 已实现（10 工具定义 + web 分类 + OpenAPI schema 输出）

**已实现:**
- 10 个工具定义：list_files / read_file / write_file / patch_file / shell_exec / git_diff / web_fetch / web_search / open_browser / file_search
- 分类：fs / shell / vcs / **web**
- 权限等级：low / medium / high
- 工具描述全面压缩（30-50% 更短）
- ToolRegistry: 注册、查询、分类筛选、OpenAI schema 输出
- wrapper: ToolRegistryLayerApi 公开接口

## 11 Executor

**状态**: v4.0 — 已实现（10 真实工具 + 3 层 Guard + URL Guard + 统一入口）

**已实现:**
- tools.py: 10 个真实工具（list_files / read_file / write_file / patch_file / shell_exec / git_diff / web_fetch / web_search / open_browser / file_search）
- web_search: ddgs 库为主 + HTTP 直搜后备（v7.0）
- guard.py: Guard 统一入口（自动识别工具类别运行对应 guard，含 _check_url SSRF 防护）
- policy/url_guard: SSRF 防护（拦截 localhost/127.0.0.1/私有 IP）
- policy/permission_guard.py: low/medium/high 三级权限检查
- policy/path_guard.py: workspace 路径边界检查
- policy/command_guard.py: 危险命令阻止 + 白名单放行
- execute_tool.py: 真实工具执行（guard → 执行 → 结果返回）
- wrapper: ExecutorLayerApi（自动订阅 + sync 执行）

## Shared

**状态**: 已实现（脚手架 3.0）

**已实现:**
- types: RunTask、TaskStatus
- errors: CatnipError、QueueError、WorkerError、GatewayError、HarnessError
- logger: get_logger（控制台日志）
- utils: create_id
- version: 版本号从 pyproject.toml 单一真相源读取
- cli: Claude Code 风格 CLI（print_step_claude / print_result_claude / print_summary_claude / print_thinking / print_streaming_answer）+ 粉红开机动画（_pink）
- interactive: ThreadPoolExecutor 后台 agent + 实时注入 + 线程安全 EventBus
- jsonl_logger: EventBus 全事件旁路写入 logs/catnip.jsonl
- webui_server: 静态页面托管 + `/api/chat` 桥接 + 后台线程 agent 执行 + 实时思考轮询 + 会话清空（Web UI v1 已完成 ✅）
