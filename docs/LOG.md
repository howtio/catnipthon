# Construction Log

> 施工日志。按版本归档到 `docs/logs/`。
> 本文件只保留索引 + 最近 3 条记录。

---

## 日志归档

| 版本 | 文件 |
|------|------|
| 0.0 | `docs/logs/LOG-0.0.md` |

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
- **下一步**: Phase 3 — Runner + EventBus 完善（tool.call.requested/result 路由）

### 2026-05-23 / Phase 1 / Gateway + Queue + Worker 最小链路

- **版本**: `0.1`
- **改动部分**:
  - `src/shared/` — 基础类型（RunTask, TaskStatus）、错误体系（CatnipError 五子类）、logger、utils（create_id）
  - `02-queue` — QueueLayerApi：asyncio FIFO 队列、入队/出队、任务状态管理（pending→running→done/failed）、completion event 等待
  - `03-worker` — WorkerLayerApi：消费循环、调用 Harness、错误捕获与状态标记
  - `01-gateway` — GatewayLayerApi：CLI 参数解析、RunTask 创建、提交 Queue、等待并返回结果
  - `04-harness` — HarnessLayerApi 占位：接受 RunTask、标记 done、返回占位结果
  - `src/bootstrap.py` — 依赖组装（App dataclass）
  - `src/main.py` — 异步启动入口（python -m src.main）
- **修改文件**: src/__init__.py, src/layers/__init__.py, src/shared/*, src/layers/{gateway_01,queue_02,worker_03,harness_04}/*, src/bootstrap.py, src/main.py, tests/test_queue.py
- **验证**: mypy 通过（17 文件 0 问题），pytest 9/9 通过，冒烟测试通过（`python -m src.main "phase1 smoke test"` 全链路跑通）
- **下一步**: Phase 2 — Harness + Context + Skills + Memory

### 2026-05-23 / Phase 0 / 骨架 2.0 — Python 工程化与目录命名修复

- **版本**: `0.0`（骨架 2.0）
- **改动部分**: 
  - 目录命名：`01-gateway` → `gateway_01`、`02-queue` → `queue_02` 等（名称_数字，标准 Python import 可用）
  - Python 工程化：新增 `pyproject.toml`（mypy strict / pytest / openai 依赖）
  - 虚拟环境：`.venv/` + ONBOARD.md 设置说明
  - API Key 管理：`apikey.txt`（用户真实 key，gitignore）+ `apikey.txt.example`（模板，进仓库）
  - Import 策略：CODEX_ARCHITECTURE.md 新增标准导入章节（`from src.layers.queue_02 import ...`）
  - 文档修订：CLAUDE.md 开工流程补 venv+apikey 步骤，CODEX_RULES_GIT.md 修正仓库 URL，DEV_PROGRESS.md 升级到骨架 2.0
- **修改文件**: CLAUDE.md、ONBOARD.md、CODEX_ARCHITECTURE.md、CODEX_MASTER_REQUIREMENTS.md、CODEX_RULES_GIT.md、docs/DEV_PROGRESS.md、docs/LOG.md、.gitignore、pyproject.toml、apikey.txt.example、11 层 README.md（目录移动）
- **验证**: mypy 无可检测代码（纯骨架），pytest 无可执行测试
- **教训**: 连字符目录 Python 无法 import；数字前缀也不行（语法错误）；`name_XX`（名称_数字）是唯一同时满足排序和 Python import 的方案；骨架阶段就该有 pyproject.toml 和 venv；API key 用根目录 txt + .gitignore 最方便
- **下一步**: Phase 1 实现 Gateway + Queue + Worker

### 2026-05-23 / Phase 0 / 项目文档骨架初始化

- **版本**: `0.0`
- **改动部分**: 项目文档体系创建（无代码，纯文档骨架）
- **修改文件**: ONBOARD.md、CODEX_MASTER_REQUIREMENTS.md、CODEX_ARCHITECTURE.md、CODEX_RULES_GIT.md、CODEX_RULES_TESTING.md、CODEX_SESSION_CONTRACT_TEMPLATE.md、docs/*、11 层 README.md、5 个 SKILL.md
- **验证**: 未执行（无代码可测）
- **下一步**: 初始化 Python 基础文件，进入 Phase 1
