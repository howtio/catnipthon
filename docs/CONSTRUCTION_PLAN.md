# Construction Plan：从 0 到 MVP 的完整施工路线

> 本文档是"非代码人也能用"的施工地图。
> 每个 Phase 明确：要做什么、创建哪些文件、怎么验证、做到什么算完成。
> 按顺序执行，不跳步，不提前做后面的。

---

## 总体路线

```
Phase 0 (0.0) ──→ 文档骨架 ✅ 当前
Phase 1 (0.1) ──→ Gateway + Queue + Worker
Phase 2 (0.2) ──→ Harness + Context + Skills + Memory
Phase 3 (0.3) ──→ Runner + EventBus
Phase 4 (0.4) ──→ Tool Registry + Executor 骨架
Phase 5 (0.5) ──→ 最小工具集
Phase 6 (0.6) ──→ DeepSeek 接入 + tool calling
Phase 7 (0.7) ──→ 日志、验收、final report
─────────────────────────────────────────
1.0 (MVP)  ──→ 全链路可跑，通过验收任务
```

---

## Phase 0：项目骨架（0.0）✅ 已完成

**目标：** 目录结构 + 全部开发文档 + 进度追踪体系。

**创建文件：**
- `ONBOARD.md`、`CODEX_MASTER_REQUIREMENTS.md`、`CODEX_ARCHITECTURE.md`
- `CODEX_RULES_GIT.md`、`CODEX_RULES_TESTING.md`
- `CODEX_SESSION_CONTRACT_TEMPLATE.md`
- `docs/DEV_PROGRESS.md`、`docs/LOG.md`、`docs/LAYER_STATUS.md`
- `docs/TOOL_POLICY.md`、`docs/AGENT_LOOP.md`、`docs/DEBUG_GUIDE.md`
- `docs/CONSTRUCTION_PLAN.md`（本文件）
- `.env.example`、`.gitignore`
- 11 层 `README.md`、5 个 `SKILL.md`

**验收标准：**
- [x] 目录结构完整
- [x] 所有文档存在且一致
- [x] `docs/LOG.md` 已记录本次施工

---

## Phase 1：Gateway + Queue + Worker（0.1）

**目标：** 打通 CLI 输入 → 任务创建 → 入队 → 消费的最小链路。

**要做什么：**

1. 初始化 Python 项目：`pyproject.toml`、安装 `mypy`、`pytest`、`openai`
2. 创建 `src/shared/` — types、logger、errors、utils
3. 创建 `src/bootstrap.py` — 依赖组装
4. 创建 `src/main.py` — 启动入口
5. 实现 02-queue — 内存 FIFO、入队/出队、任务状态 pending/running/done/failed
6. 实现 03-worker — 消费循环、调用 Harness（先传占位）、错误捕获
7. 实现 01-gateway — CLI 参数解析、创建 RunTask、提交 Queue、等待结果

**关键约束：**
- Queue 只管存/取/状态，不管线程池（线程池归 Worker）
- Worker 不构建 prompt，不调模型，不执行工具
- Gateway 不调模型，不执行工具，不读写 workspace

**验收标准：**
- [ ] `mypy src/` 通过
- [ ] `python -m src.main "phase1 smoke test"` 能创建任务并入队出队
- [ ] 新增 `tests/test_queue.py` 至少 2 个测试通过
- [ ] `docs/LOG.md` 已追加记录（版本号 `0.1`）
- [ ] git push

---

## Phase 2：Harness + Context + Skills + Memory（0.2）

**目标：** 补齐 run 生命周期管理、文档装载、技能注入、记忆读写。

**要做什么：**

1. 实现 05-context — 读取 docs/、扫描 workspace、构建 system prompt、提取开工清单
2. 实现 06-skills — 技能注册表、关键词匹配、SKILL.md 加载、注入
3. 实现 07-memory — session 记忆维护、working memory、持久化到 `logs/catnip-memory.json`
4. 实现 04-harness — 串联 Context → Skills → Memory → Runner（仍然是占位）、run 生命周期、final report 骨架
5. 实现 09-eventbus — 事件发布订阅（先用 Python asyncio.Event 或简单回调）

**关键约束：**
- Context 不修改 workspace，不执行 shell
- Skills 不执行文件读写，不调 Executor
- Memory 不读写 workspace 业务文件，不调模型
- Harness 不直接执行工具

**验收标准：**
- [ ] `mypy src/` 通过
- [ ] Harness 能生成包含 system prompt + skills + memory 的上下文
- [ ] `python -m src.main "phase2 smoke test"` 能输出 run 生命周期事件
- [ ] 新增测试至少 4 个通过
- [ ] `docs/LOG.md` 已追加记录（版本号 `0.2`）
- [ ] git push

---

## Phase 3：Runner + EventBus（0.3）

**目标：** 建立受控 ReAct Loop 骨架，让 Runner 能通过 EventBus 发起工具请求并等待结果。

**要做什么：**

1. 完善 09-eventbus — 实现 `publish`、`subscribe`、`waitForToolResult`
2. 实现 08-runner — heuristic provider（规则路由）、step 计数、工具请求/结果处理循环
3. 实现 10-tool-registry — 工具定义注册（先用元数据占位）
4. 实现 11-executor 骨架 — 监听 tool.call.requested、返回模拟结果

**关键约束：**
- Runner 不 import Executor
- Runner 不直接读写文件
- Runner 只能通过 EventBus 发起 `tool.call.requested`

**验收标准：**
- [ ] `mypy src/` 通过
- [ ] Runner 能发起 `tool.call.requested` 事件并收到 `tool.call.result`
- [ ] EventBus 支持 `waitForToolResult`
- [ ] 新增测试至少 3 个通过
- [ ] `docs/LOG.md` 已追加记录（版本号 `0.3`）
- [ ] git push

---

## Phase 4：Tool Registry + Executor 骨架（0.4）

**目标：** 补齐工具元数据和 Executor 执行前准入检查。

**要做什么：**

1. 完善 10-tool-registry — 注册 6 个工具定义（list_files/read_file/write_file/patch_file/shell_exec/git_diff），含 category、参数 schema、权限等级
2. 完善 11-executor — guard 统一入口（permissionGuard/pathGuard/commandGuard 占位），监听工具请求，返回成功或失败事件
3. 更新 09-eventbus 事件类型，支持 `tool.call.failed`

**关键约束：**
- Tool Registry 只说明"工具是什么"，不执行
- Executor 是唯一副作用边界
- Guard 必须先于执行

**验收标准：**
- [ ] `mypy src/` 通过
- [ ] Tool Registry 能返回工具定义给 AI SDK
- [ ] Executor guard 能拦截未注册工具
- [ ] `python -m src.main "phase4 guard test"` 通过
- [ ] 新增测试至少 2 个通过
- [ ] `docs/LOG.md` 已追加记录（版本号 `0.4`）
- [ ] git push

---

## Phase 5：最小工具集（0.5）

**目标：** 实现 6 个工具的真实执行 + 3 层 guard。

**要做什么：**

1. 实现 `list_files` — 目录读取
2. 实现 `read_file` — 文件读取
3. 实现 `write_file` — 文件写入
4. 实现 `patch_file` — 字符串替换
5. 实现 `shell_exec` — shell 命令执行（白名单）
6. 实现 `git_diff` — 只读 git diff
7. 实现 permissionGuard — low/medium/high 三级权限
8. 实现 pathGuard — workspace 边界检查
9. 实现 commandGuard — 危险命令阻止 + 白名单放行

**验收标准：**
- [ ] `mypy src/` 通过
- [ ] 6 个工具每个至少 1 个测试通过
- [ ] guard 拦截测试通过（越权、越界、危险命令）
- [ ] `python -m src.main "list files and read readme"` 冒烟通过
- [ ] `docs/LOG.md` 已追加记录（版本号 `0.5`）
- [ ] git push

---

## Phase 6：DeepSeek 接入 + Tool Calling（0.6）

**目标：** 把真实模型接到 Runner，打通 AI SDK tool calling 链路。

**要做什么：**

1. 实现 deepseek provider — 通过 openai Python SDK 调用 DeepSeek API
2. 实现 heuristic provider fallback — 无 key 时用规则路由
3. Runner 改用 `runWithTools` 模式 — 模型决定是否调工具
4. 实现多步工具计划和最终回答生成
5. 从 `.local-secrets/deepseek.env` 加载 key

**验收标准：**
- [ ] `mypy src/` 通过
- [ ] 无 key 时 heuristic provider 正常工作
- [ ] 有 key 时 DeepSeek 单轮调用成功
- [ ] DeepSeek tool calling 链路跑通（模型发起工具请求 → Executor 执行 → 结果返回模型）
- [ ] `python -m src.main "readme and git diff"` 通过
- [ ] 新增测试至少 3 个通过
- [ ] `docs/LOG.md` 已追加记录（版本号 `0.6`）
- [ ] git push

---

## Phase 7：日志、验收、Final Report（0.7）

**目标：** JSONL 事件日志、run report 落盘、CI 可运行。

**要做什么：**

1. 实现 JSONL 日志 — `logs/catnip.jsonl`，EventBus 所有事件旁路写入
2. 实现 trace 日志 — `logs/catnip-trace.jsonl`，prompt/plan/reasoning
3. Harness final report — 包含 stepsUsed、finalAnswer、toolSummaryCount、修改文件列表
4. CLI 输出 — runId、steps、toolSummaryCount、durationMs、finalAnswer
5. 完善测试 — 所有层至少 1 个测试
6. 验收链路 — Gate → Queue → Worker → Harness → Context → Skills → Memory → Runner → EventBus → Tool Registry → Executor 全链路可观测

**验收标准：**
- [ ] `mypy src/` 通过
- [ ] `pytest` 全部通过
- [ ] `logs/catnip.jsonl` 记录完整工具调用链路
- [ ] 验收任务跑通（见下方）

**MVP 验收任务：**
```bash
python -m src.main "在 workspace/demo 中创建 src/add.py，实现 add(a, b) 函数，创建测试文件，运行测试，输出修改摘要、风险和回滚方案"
```

**全链路必须经过：**
```
Gateway 创建任务 → Queue 入队 → Worker 消费 → Harness 创建 run
→ Context 构建上下文 → Skills 注入 → Memory 注入
→ Runner 调模型 → EventBus 请求 list_files → Executor 执行
→ EventBus 请求 read_file → Executor 执行
→ EventBus 请求 write_file → Executor 执行
→ EventBus 请求 shell_exec(pytest) → Executor 执行
→ Harness 强制 git_diff → Harness 输出 final report
→ Worker 标记 done → 结果回显 CLI
```

---

## 1.0（MVP）

**标记条件：** Phase 0-7 全部完成 + 验收任务通过。

**之后：** 等用户检查拍板，宣布 `2.0` 方向。
