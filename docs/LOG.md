# Construction Log

> 施工日志。按版本归档到 `docs/logs/`。
> 本文件只保留索引 + 最近 3 条记录。

---

## 日志归档

| 版本 | 文件 |
|------|------|
| 0.0 | `docs/logs/LOG-0.0.md` |
| 0.1 | `docs/logs/LOG-0.0.md`（已剥离） |
| 0.2 | `docs/logs/LOG-0.0.md`（已剥离） |
| 1.0 | `docs/logs/LOG-1.0.md` |
| 2.0 | `docs/logs/LOG-2.0.md` |

---

## 日志模板

```markdown
## YYYY-MM-DD / Phase X / 标题

### 版本
- `0.x`

### 目标
本次施工目标。

### 开工检查
- 当前分支、备份分支名、备份提交号

### 本次修改
- 修改点 1

### 改动部分
- 模块：做了什么

### 修改文件
- file1

### 验证结果
- mypy src/：通过 / 失败
- pytest：通过 / 失败
- 冒烟测试：通过 / 未执行

### 回滚判断
- 是否发生需要回滚的错误
- 如需回滚，回滚目标提交号

### 风险
- 风险 1

### 下一步
下一步计划。
```

---

## 最近记录

### 2026-05-24 / v7.0 — 搜索增强 + CLI 交互大修

- **版本**: `7.0`
- **改动部分**:
  - **web_search 全面翻新**:
    - `duckduckgo_search` → `ddgs` 迁移（消除 RuntimeWarning）
    - 新增 `_search_ddg_html()` HTTP 后备搜索（httpx + BeautifulSoup 直接抓取 DDG 结果页）
    - 双后备策略：ddgs 库为主，HTTP 直搜为辅，任一成功即可
    - pyproject.toml 依赖更新：`duckduckgo-search` → `ddgs`
  - **CLI 思考显示重写**:
    - `print_thinking()` 过滤无意义内容（跳过单标点/空白碎片），只显示真实推理文字
    - 新增 `print_streaming_answer()` — 最终答案实时流式显示
    - 新增 `AGENT_ANSWER_CHUNK` 事件类型，最终答案按 60 字符分段推送
    - 新增 `_is_meaningful()` 智能判断（CJK 或 2+ 字母词才显示）
    - `warnings.filterwarnings("ignore")` 抑制 Python 包警告
  - **System Prompt 优化**:
    - 优先 write_file/read_file 操作文件，shell_exec 仅用于安装/测试
    - HTML 结果用 open_browser 展示，不用 shell
  - **依赖更新**:
    - `duckduckgo-search>=7.0` → `ddgs>=9.0`
- **修改文件**:
  - `pyproject.toml` — 版本 7.0 + ddgs 依赖
  - `src/layers/executor_11/tools.py` — web_search 双后备重写
  - `src/layers/eventbus_09/event_types.py` — 新增 AGENT_ANSWER_CHUNK
  - `src/layers/runner_08/deepseek_provider.py` — 最终答案分段推送
  - `src/shared/cli.py` — print_thinking 过滤 + print_streaming_answer
  - `src/shared/interactive.py` — 流式答案展示 + 警告抑制
  - `src/layers/context_05/build_base_system_prompt.py` — shell_exec 约束
- **验证**: mypy 95 文件 0 错误，pytest 70/70 通过
- **下一步**: 等待用户反馈

- **版本**: `5.0`
- **改动部分**:
  - **流式超时**（根治卡死）:
    - `deepseek_provider.py` — `client.chat.completions.create()` 加 `timeout=60`，流停滞超过 60s 抛 APITimeout，不再永久挂起
  - **Web 搜索替换为 duckduckgo_search 库**:
    - 移除脆弱的手动 HTML 正则解析（`class="result__a"` 等）
    - `web_search` 改用 `duckduckgo_search.DDGS.text()`，更稳定、更干净
  - **Web 抓取替换为 BeautifulSoup**:
    - `_fetch_url` 用 `BeautifulSoup.get_text()` 代替 `re.sub(r"<[^>]+>")`，正确移除 script/style
  - **open_browser 结果引导**:
    - 成功消息追加 "Continue with the next step."，agent 知道要继续
  - **max_steps 提升**: 10 → 20（默认），15 → 20（run_lifecycle）
  - **依赖加固**: httpx / beautifulsoup4 / duckduckgo-search 正式加入 pyproject.toml
- **修改文件**:
  - `pyproject.toml` — 版本 5.0 + 新增依赖
  - `src/layers/runner_08/deepseek_provider.py` — timeout=60
  - `src/layers/executor_11/tools.py` — 重写 web_search/_fetch_url/open_browser，移除 import re
  - `src/layers/runner_08/types.py` — max_steps 10→20
  - `src/layers/harness_04/run_lifecycle.py` — max_steps 15→20
  - `tests/test_deepseek_provider.py` — timeout 断言
- **验证**: mypy 95 文件 0 错误，pytest 70/70 通过
- **提交**: （待 commit）
- **下一步**: 等待用户反馈

### 2026-05-24 / v4.0 — 工具增强 + 会话记忆 + Token 优化

- **版本**: `4.0`
- **改动部分**:
  - **模型切换**: `deepseek-reasoner` → `deepseek-chat`（修复工具调用卡死 + 系统消息原生支持 + 大幅减少 token）
  - **新增 4 个工具**:
    - `web_fetch(query)` — httpx URL 抓取 + HTML 标签剥离，10KB 限制，15s 超时
    - `web_search(query, max_results=5)` — DuckDuckGo HTML 搜索，正则解析标题/链接/摘要
    - `open_browser(url)` — Python webbrowser.open，仅允许 http/https
    - `file_search(pattern, content, max_results)` — 名称 glob 或内容 grep，跳过 .venv/.git/__pycache__
  - **Token 优化**:
    - 工具描述全面压缩 30-50%
    - `_compress_history()` — 旧 tool 结果截断为 500 字符
    - `_truncate()` — 工具结果限制 2000 字符
  - **会话记忆**: `SessionMemory` 进程内跟踪 files_read/files_written/tool_counts/user_notes，自动注入 system prompt
  - **安全增强**: `_check_url()` SSRF 防护（拦截 localhost/127.0.0.1/169.254./10./172.16./192.168.）
  - **新分类**: ToolCategory 新增 `"web"` 类型
  - **工具总量**: 6 MVP → 10 个
- **修改文件**:
  - `src/layers/runner_08/deepseek_provider.py` — 模型切换 + 历史压缩 + 结果截断
  - `src/layers/executor_11/tools.py` — 新增 4 个 web/file 工具
  - `src/layers/executor_11/guard.py` — 新增 _check_url SSRF 防护
  - `src/layers/executor_11/execute_tool.py` — 注册 10 个工具实现
  - `src/layers/tool_registry_10/types.py` — 新增 web 分类
  - `src/layers/tool_registry_10/tool_registry.py` — 注册 10 个工具
  - `src/layers/tool_registry_10/tools/*.py` — 工具描述压缩
  - `src/layers/memory_07/session_memory.py` — 新建 SessionMemory
  - `src/layers/memory_07/wrapper.py` — 集成 SessionMemory
  - `src/layers/harness_04/run_lifecycle.py` — 注入 session 上下文 + 跟踪工具调用
  - `tests/test_tools_v4.py` — 新建 6 个工具测试
  - `tests/test_guards.py` — 新增 3 个 URL 守卫测试
  - `tests/test_tool_registry.py` — 更新 6→10 工具断言
  - `tests/test_deepseek_provider.py` — 更新 system prompt 断言
- **验证**: mypy 95 文件 0 错误，pytest 69/69 通过
- **提交**: 9f581be
- **下一步**: 等待用户反馈，规划 5.0 方向

### 2026-05-24 / v3.0 — 队列层重构 + 推理路径显示 + CLI 视觉升级

- **版本**: `3.0`
- **改动部分**:
  - **Phase 1 — 队列层重构**:
    - `types.py` — RunTask 新增 `appended_requirements`、`last_heartbeat_at` 字段
    - `in_memory_queue.py` — 新增 `threading.Event` 驱动 `wait_for_task()` 阻塞等待
    - `task_status_store.py` — 新增 `append_requirement`、`update_heartbeat`、`get_stale_tasks`、`get_running`
    - `wrapper.py` — QueueLayerApi 暴露 `wait_for_task`、`append_requirement`、`update_heartbeat`、`get_stale_tasks`、`get_running_tasks`
    - `event_types.py` — 新增 `QUEUE_HEARTBEAT`
    - `run_worker_loop.py` — 重写为阻塞等待 + try/except 错误处理
    - `wrapper.py` (worker) — 新增 `run_with_heartbeat` 后台心跳线程
    - 删除死代码：`process_run_task.py`、`handle_worker_error.py`
    - `deepseek_provider.py` — 主循环中消费 `task.appended_requirements`
  - **Phase 2 — 推理路径 + 层颜色**:
    - `deepseek_provider.py` — 切换模型 `deepseek-reasoner`，捕获 `reasoning_content` 发布为 `AGENT_REASONING_CHUNK`
    - `event_types.py` — 新增 `AGENT_REASONING_CHUNK`
    - `cli.py` — 新增 `LAYER_COLORS` 字典、`layer_color()`、`c_layer()` 辅助函数
    - `interactive.py` — ProgressTracker 订阅 `AGENT_REASONING_CHUNK`，实时显示推理文本（青色 96）
  - **Phase 3 — 视觉大修**:
    - `cli.py` — 新增粉红支持（`PINK=213`、`_is_256color()`、`_pink()`）
    - `print_header()` — 全粉红开机动画
    - `_layer_lines()` — 各层名以 `LAYER_COLORS` 固定颜色着色
    - `print_step_header()` — 使用 runner 层颜色（33）
    - `print_session_summary()` — 使用 harness 层颜色（92）
- **验证**: mypy 90 文件 0 问题，pytest 60/60 通过
- **提交**: 2c1fc43
- **下一步**: 等待用户反馈

### 2026-05-24 / v3.1 — 线程池 + Claude Code CLI + 实时注入

- **版本**: `3.1`
- **改动部分**:
  - **线程安全基础**:
    - EventBus 全面加锁（threading.Lock）保护 _subscribers、_history、_waiters
    - TaskStatusStore 全面加锁，保证跨线程安全
  - **Claude Code CLI 风格**:
    - 移除随机颜色，改用固定专业调色板（OK=32, ERROR=91, HIGHLIGHT=96, DIM=90）
    - 新增 `print_step_claude()`、`print_result_claude()`、`print_summary_claude()`、`print_thinking()`
    - 使用 ◇ ┃ ✓ 符号，去除随机噪声
  - **线程池 + 后台执行**:
    - ThreadPoolExecutor(max_workers=1) 在后台线程运行 agent
    - 主线程持续接受输入，任务运行时自动转为注入模式
    - 任何非命令文本自动通过 append_requirement 注入
    - 移除 AGENT_ASKING_USER / AGENT_USER_RESPONSE 事件
    - 移除 _check_for_user_input()，简化 RunnerConfig
- **验证**: mypy 90 文件 0 问题，pytest 60/60 通过
- **提交**: （当前）
- **下一步**: 等待用户反馈

### 2026-05-24 / CLI 2.0 — 交互式 REPL + 实时进度 + DeepSeek 真实环境测试

- **版本**: `2.0`
- **改动部分**:
  - `shared/interactive.py` — 新增交互式 REPL：提示符、内部命令（/exit /help /provider /clear /history）、ProgressTracker（通过 EventBus 订阅实时显示 tool 调用过程）
  - `shared/cli.py` — 更新 H_LINE/EQUAL_LINE 常量，Unicode 框线改用转义序列兼容
  - `main.py` — 无参数时启动交互式 REPL，有参数时保持批量模式；Windows GBK 编码兼容
  - DeepSeek 真实环境测试通过（中文提问 → tool calling → 中文回答全链路可跑）
- **验证**: mypy 92 文件 0 问题，pytest 60/60 通过
- **提交**: （待 commit）
- **下一步**: 等待用户反馈，规划 3.0 方向


### 2026-05-24 / 1.0 MVP — 全链路可跑，通过验收任务

- **版本**: `1.0`
- **改动部分**:
  - 修复 deepseek provider 的 tool_calls 消息顺序 bug（assistant 消息应在所有 tool 结果之前）
  - RunnerConfig 支持 `CATNIP_RUNNER_PROVIDER` 环境变量选择 provider
  - CLI 输出兼容 Windows GBK 编码（fallback to UTF-8）
  - `deepseek_provider.py` 多轮 tool calling 链路完全打通
- **验证**: mypy 91 文件 0 问题，pytest 60/60 通过
  - 验收任务："在 workspace/demo 中创建 src/add.py，实现 add(a, b) 函数，创建测试文件，运行测试"
  - DeepSeek 15 步循环：list_files → read_file(x6) → shell_exec(x5) → git_diff → 最终回答
  - 全链路：Gateway→Queue→Worker→Harness→Context→Skills→Memory→Runner→EventBus→Tool Registry→Executor
  - JSONL 事件日志完整记录 `logs/catnip.jsonl`
- **回滚判断**: 无阻塞性错误。Windows GBK _readerthread 警告不影响功能。
- **下一步**: 等待用户检查拍板，宣布 2.0 方向


### 2026-05-24 / Phase 7 — 日志、验收、final report

- **版本**: `0.7`
- **改动部分**:
  - `shared/jsonl_logger.py` — 新增 JSONL 事件日志（所有 EventBus 事件旁路写入 `logs/catnip.jsonl`）
  - `runner_08/agent_runner.py` — 新增发布 AGENT_PLAN_GENERATED / AGENT_REASONING_SUMMARY 事件
  - `runner_08/deepseek_provider.py` — 同上，DeepSeek provider 也发布规划/推理事件
  - `harness_04/run_lifecycle.py` — 自动收集 tool_summary（工具计数）、modified_files（写文件列表）、精确 step count
  - `harness_04/build_final_report.py` — 输出包含工具摘要行（如 "Tools used: list_files (1), git_diff (1)"）
  - `bootstrap.py` — 附加 JSONL logger 到 EventBus
- **验证**: mypy 91 文件 0 问题，pytest 60/60 通过，冒烟测试通过（JSONL 14 条事件记录完整）
- **提交**: （待 commit）
- **下一步**: 1.0 MVP — 验收任务跑通


### 2026-05-24 / Phase 6 — DeepSeek 接入 + tool calling

- **版本**: `0.6`
- **改动部分**:
  - `runner_08/deepseek_provider.py` — 基于 OpenAI SDK 的 DeepSeek API 完整多轮 tool calling 实现
  - `runner_08/agent_runner.py` — 支持 provider 切换（cfg.provider == "deepseek" 时走 DeepSeek）
  - `runner_08/wrapper.py` — `run()` 新增 `system_prompt` 参数并转发
  - `harness_04/run_lifecycle.py` — 构建 full_prompt（enhanced_prompt + memory_block）传递给 runner
  - 新增测试 7 个（无 key 回退、client 管理、API 错误、无工具作答、system_prompt 传递、max_steps 终止）
- **验证**: mypy 90 文件 0 问题，pytest 60/60 通过
- **提交**: （待 commit）
- **下一步**: Phase 7 — 日志、验收、final report 增强


### 2026-05-24 / Phase 5 — 实现 6 个真实工具 + 3 层 Guard

- **版本**: `0.5`
- **改动部分**:
  - `executor_11/tools.py` — 6 个真实工具实现：list_files（目录列表）、read_file（文件读取）、write_file（文件写入）、patch_file（字符串替换）、shell_exec（shell 命令执行）、git_diff（git diff）
  - `executor_11/policy/permission_guard.py` — low/medium/high 三级权限
  - `executor_11/policy/path_guard.py` — workspace 边界检查
  - `executor_11/policy/command_guard.py` — 白名单 + 危险命令阻止
  - `executor_11/guard.py` — Guard 统一入口（自动识别工具类别运行对应 guard）
  - `executor_11/execute_tool.py` — 更新为真实执行 + guard 检查
- **验证**: mypy 89 文件 0 问题，pytest 53/53 通过，冒烟测试通过（真实 list_files + read_file 执行成功）
- **提交**: dd36bd4
- **下一步**: Phase 6 — DeepSeek 接入 + Tool Calling


### 2026-05-24 / Phase 3+4 — Runner + EventBus + Tool Registry + Executor 骨架

- **版本**: `0.4`
- **改动部分**:
  - `09-eventbus` — 新增waitForToolResult（threading.Event 实现工具结果等待）
  - `10-tool-registry` — 完整实现：6 个工具定义（list_files/read_file/write_file/patch_file/shell_exec/git_diff）、OpenAI schema 输出
  - `11-executor` — 骨架实现：订阅 tool.call.requested、模拟执行、发布 tool.call.result/failed
  - `08-runner` — 完整实现：heuristic provider、计划生成、agent 循环、工具请求/结果处理
  - `04-harness` — Runner 实现替换占位，真实调用 agent loop
  - `bootstrap.py` — Wire 全部 11 层
  - 新增测试 11 个（runner 3、executor 3、tool_registry 5、waitForToolResult 3，但实际新增只 11 个）
- **验证**: mypy 83 文件 0 问题，pytest 38/38 通过，冒烟测试通过（Runner heuristic: list_files + git_diff 计划执行）
- **提交**: f581ed2
- **下一步**: Phase 4 — Tool Registry 完善 + Executor Guard 框架


### 2026-05-24 / Phase 2 — Harness + Context + Skills + Memory + EventBus

- **版本**: `0.2`
- **改动部分**:
  - `09-eventbus` — 完整实现：EventBus pub/sub、事件类型常量、历史记录、订阅/取消订阅
  - `05-context` — 完整实现：文档加载、Workspace 扫描、System Prompt 构建、开工清单提取
  - `06-skills` — 完整实现：技能注册表、关键词匹配、SKILL.md 加载、注入
  - `07-memory` — 完整实现：MemorySnapshot、WorkingSet、JSON 持久化、session 记忆维护
  - `04-harness` — 完整实现：Run 生命周期、Context→Skills→Memory→Runner 串联、Final Report
  - `08-runner` — 占位符（Phase 3+4 实现真实 ReAct loop）
  - `bootstrap.py` — Wire 全部 8 层
  - 新增测试 20 个（eventbus 5、context 4、skills 5、memory 4、harness 2）
- **验证**: mypy 65 文件 0 问题，pytest 24/24 通过，冒烟测试通过（Context 8 docs + Skills: testing + Memory: 187 chars）
- **提交**: 43cf920
- **下一步**: Phase 3+4 — Runner + EventBus 完善（tool.call.requested/result 路由）

### 2026-05-24 / Phase 1 — Gateway + Queue + Worker 最小链路打通

- **版本**: `0.1`
- **改动部分**:
  - `02-queue` — 完整实现：InMemoryQueue（FIFO deque）、TaskStatusStore、enqueue/dequeue 逻辑、QueueLayerApi wrapper
  - `03-worker` — 完整实现：WorkerLoop 同步消费循环、process_run_task（可注入 callable）、mark_task_status、handle_worker_error、WorkerLayerApi wrapper
  - `01-gateway` — 完整实现：CLI 参数解析（argparse）、ValidateUserInput、create_run_task（UUID）、GatewayLayerApi wrapper
  - `bootstrap.py` — Wire Gateway + Queue + Worker 三层
  - `main.py` — 更新入口：接收 CLI 参数 → 走完整 pipeline
  - 新增测试 `tests/test_queue.py` — 4 个测试
- **验证**: mypy 39 文件 0 问题，pytest 4/4 通过，冒烟测试通过
- **提交**: 5736ec6
- **下一步**: Phase 2 — Harness + Context + Skills + Memory



### 2026-05-23 / Windows 特化 — catnipthon 全面 Windows 优先适配

- **版本**: `0.0`（Windows 特化脚手架 3.0）
- **改动部分**:
  - 文档修复：README 版本号修正、11 层 README 目录名修正、LOG 归档、Phase 回滚历史标注
  - Windows 特化：路径改为 Windows 优先（`\`）、`.venv\Scripts\` 首要路径、PowerShell API Key 加载
  - 浏览器默认命令设为 `start`（Windows）
  - CLAUDE.md / ONBOARD.md / 各文档全面同步 Windows 优先指令
  - 主线仓库标注：`https://github.com/howtio/catnipthon`
- **修改文件**: 21 个文档文件修复 + 5 个文件 Windows 特化
- **验证**: mypy 通过（shared 组件）
- **下一步**: Phase 1 — Gateway + Queue + Worker

### 2026-05-23 / 脚手架 3.0 — 马拉松接力 + 防漂移 + CLI开机动画组件化

- **版本**: `0.0`（脚手架 3.0）
- **改动部分**:
  - 剥离所有 Phase 1/2 实现代码，回归纯脚手架状态
  - CLI 开机动画组件化：`src/shared/cli.py`（TITLE/SUBTITLE/LAYERS 可覆盖）
  - 版本管理：`src/shared/version.py`（pyproject.toml 单一真相源）
  - 马拉松自动接力规则：CLAUDE.md 新增最高优先级规则
  - 文档防漂移机制：收尾流程新增版本同步 + 漂移检查步骤
  - CLI 风格文档：`docs/CLI_STYLE.md`
  - ONBOARD.md：架构图命名修正 + §13 脚手架复用指南
  - 层 __init__.py 清空为占位符，bootstrap.py/main.py 简化为脚手架模板
  - 删除所有测试文件和 Session Contract（纯脚手架不需要）
- **修改文件**: 删除 17 个实现文件，重写 5 个文档 + bootstrap/main
- **验证**: mypy 通过（shared 组件），CLI 开机动画正常
- **下一步**: 基于脚手架 3.0 重新开始 Phase 1 施工

### 2026-05-23 / Phase 2 / Harness + Context + Skills + Memory + EventBus

- **版本**: `0.2`
- **改动部分**:
  - `09-eventbus` — 异步 pub/sub 事件系统（publish/subscribe/unsubscribe），事件类型常量
  - `05-context` — 文档加载（ONBOARD/CLAUDE/ARCHITECTURE）、workspace 扫描、system prompt 构建、开工清单提取
  - `06-skills` — 技能注册表、关键词匹配（5 个技能 × 多关键词）、SKILL.md 加载、默认 fallback 到 coding
  - `07-memory` — MemorySnapshot（session/working/carryover）、JSON 持久化、裁剪（max 50 session / 20 obs / 10 files）、记忆注入 prompt
  - `04-harness` — 真实编排替换占位：Context → Skills → Memory → Runner → EventBus → final report
  - `08-runner` — Phase 2 占位（返回 mock answer + 上下文长度）
  - 新增测试：eventbus 5 个、context 5 个、skills 8 个、memory 8 个、harness 3 个
- **修改文件**: src/layers/{eventbus_09,context_05,skills_06,memory_07,harness_04,runner_08}/*, src/bootstrap.py, tests/*
- **验证**: mypy 通过（28 文件 0 问题），pytest 38/38 通过，冒烟测试通过（事件发布、文档加载 16199 chars、技能匹配 "testing"、final report 生成）
- **下一步**: Phase 3+4 — Runner + EventBus 完善（tool.call.requested/result 路由）
