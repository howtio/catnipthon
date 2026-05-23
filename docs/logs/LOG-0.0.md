# 0.0 施工日志归档

## 2026-05-23 / Phase 0 / 骨架 2.0 — Python 工程化与目录命名修复

### 版本
- `0.0`（骨架 2.0）

### 目标
Python 工程化初始化 + 目录命名修复（01-gateway → gateway_01）。

### 开工检查
- 基于脚手架 1.0 继续

### 本次修改
- 目录命名：`01-gateway` → `gateway_01`、`02-queue` → `queue_02` 等（名称_数字，标准 Python import 可用）
- Python 工程化：新增 `pyproject.toml`（mypy strict / pytest / openai 依赖）
- 虚拟环境：`.venv/` + ONBOARD.md 设置说明
- API Key 管理：`apikey.txt`（用户真实 key，gitignore）+ `apikey.txt.example`（模板，进仓库）
- Import 策略：CODEX_ARCHITECTURE.md 新增标准导入章节（`from src.layers.queue_02 import ...`）
- 文档修订：CLAUDE.md 开工流程补 venv+apikey 步骤，CODEX_RULES_GIT.md 修正仓库 URL，DEV_PROGRESS.md 升级到骨架 2.0

### 改动部分
- 目录结构：全部 11 层目录重命名
- 文档：多处同步更新

### 修改文件
CLAUDE.md、ONBOARD.md、CODEX_ARCHITECTURE.md、CODEX_MASTER_REQUIREMENTS.md、CODEX_RULES_GIT.md、docs/DEV_PROGRESS.md、docs/LOG.md、.gitignore、pyproject.toml、apikey.txt.example、11 层 README.md（目录移动）

### 验证结果
- mypy：无可检测代码（纯骨架）
- pytest：无可执行测试

### 教训
连字符目录 Python 无法 import；数字前缀也不行（语法错误）；`name_XX`（名称_数字）是唯一同时满足排序和 Python import 的方案；骨架阶段就该有 pyproject.toml 和 venv；API key 用根目录 txt + .gitignore 最方便

### 回滚判断
- 无需回滚

### 风险
- 无代码可验证

### 下一步
Phase 1 实现 Gateway + Queue + Worker

## 2026-05-23 / Phase 0 / 项目文档骨架初始化

### 版本
- `0.0`

### 目标
建立 catnipthon 项目的完整文档骨架。零代码，纯文档和目录结构。

### 开工检查
- 新项目，无既有 git 历史

### 本次修改
- 创建 11 层目录结构（01-gateway ~ 11-executor）
- 编写全部开发文档：ONBOARD、CODEX_MASTER_REQUIREMENTS、CODEX_ARCHITECTURE、CODEX_RULES_GIT、CODEX_RULES_TESTING、CODEX_SESSION_CONTRACT_TEMPLATE
- 编写施工文档：CONSTRUCTION_PLAN、AGENT_LOOP、TOOL_POLICY、DEBUG_GUIDE
- 编写进度文档：DEV_PROGRESS、LOG、LAYER_STATUS
- 编写 11 层 README.md 和 5 个 SKILL.md
- 创建 CLAUDE.md（Claude Code 自动加载规则）
- 创建 .env.example、.gitignore、.local-secrets/ 目录
- 语言栈：Python（mypy + pytest + openai SDK）

### 改动部分
- 文档体系：全部文档从零创建
- 目录结构：11 层（01-11，无 06.5 补丁号）
- 技术栈：Python（非 TypeScript）

### 修改文件
- 全部 36 个文件均为新建

### 验证结果
- mypy：未执行（无代码）
- pytest：未执行（无代码）
- 文档一致性：人工检查通过

### 回滚判断
- 无需回滚（新建项目）

### 风险
- 无代码可验证

### 下一步
- Phase 1：初始化 pyproject.toml，实现 Gateway + Queue + Worker

## 2026-05-23 / Phase 1 / Gateway + Queue + Worker 最小链路

### 版本
- `0.1`

### 目标
打通 CLI 输入 → 任务创建 → 入队 → 消费的最小链路。

### 本次修改
- `src/shared/` — 基础类型（RunTask, TaskStatus）、错误体系（CatnipError 五子类）、logger、utils（create_id）
- `02-queue` — QueueLayerApi：asyncio FIFO 队列、入队/出队、任务状态管理（pending→running→done/failed）、completion event 等待
- `03-worker` — WorkerLayerApi：消费循环、调用 Harness、错误捕获与状态标记
- `01-gateway` — GatewayLayerApi：CLI 参数解析、RunTask 创建、提交 Queue、等待并返回结果
- `04-harness` — HarnessLayerApi 占位：接受 RunTask、标记 done、返回占位结果
- `src/bootstrap.py` — 依赖组装（App dataclass）
- `src/main.py` — 异步启动入口（python -m src.main）

### 修改文件
src/__init__.py, src/layers/__init__.py, src/shared/*, src/layers/{gateway_01,queue_02,worker_03,harness_04}/*, src/bootstrap.py, src/main.py, tests/test_queue.py

### 验证结果
- mypy：通过（17 文件 0 问题）
- pytest：9/9 通过
- 冒烟测试：通过（全链路跑通）

### 回滚判断
- 无需回滚（已在脚手架 3.0 中剥离回归纯骨架）

### 风险
- 此 Phase 代码已在后续重构中剥离，如需重新实现需从头开始
