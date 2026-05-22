# Development Progress

> 当前总进度快照。新会话接手时，本文件是第一个该读的进度文件。
> 详细施工记录见 `docs/LOG.md`。

---

## 当前版本

`0.1`（Phase 1 完成：Gateway + Queue + Worker）

---

## 整体状态

| 项目 | 状态 |
|------|------|
| 版本 | `0.0` |
| Phase 0（骨架 1.0：基础文档 + 目录） | 已完成 |
| Phase 0（骨架 2.0：Python 工程化 + 导入策略） | 已完成 |
| Phase 1（Gateway + Queue + Worker） | 已完成 |
| Phase 2（Harness + Context + Skills + Memory） | 未开始 |
| Phase 3（Runner + EventBus 骨架） | 未开始 |
| Phase 4（Tool Registry + Executor 骨架） | 未开始 |
| Phase 5（最小工具集） | 未开始 |
| Phase 6（DeepSeek 接入 + tool calling） | 未开始 |
| Phase 7（日志、验收、final report） | 未开始 |
| typecheck | 通过（17 文件 0 问题） |
| 测试 | 9/9 通过 |

---

## 进行中

- 无（Phase 1 已完成，等待 Phase 2）

---

## 未开始

- Phase 2：Harness + Context + Skills + Memory
- Phase 3 ~ 7

---

## 已完成

- Phase 1（2026-05-23）：Gateway + Queue + Worker 最小链路 — `python -m src.main "msg"` 全链路跑通
  - `src/shared/`：RunTask, TaskStatus, CatnipError 五子类, logger, utils
  - `02-queue`：asyncio FIFO 队列、任务状态管理、completion event
  - `03-worker`：消费循环、Harness 调用、错误捕获
  - `01-gateway`：CLI 解析、任务创建提交、结果等待
  - `04-harness`：占位实现（标记 done 并返回）
  - 测试：9 个通过（队列 FIFO、状态转换、错误处理、集成流）
- Phase 0 骨架 1.0：项目文档体系（ONBOARD.md、CODEX_*.md、施工文档、进度追踪）
- Phase 0 骨架 2.0（2026-05-23）：
  - Python 工程化：`pyproject.toml`、`.venv/` 虚拟环境、mypy strict 模式、pytest 配置
  - 目录命名：层目录使用 `gateway_01`、`queue_02` 等（名称_数字，标准 Python import 可用）
  - API Key 管理：`apikey.txt`（用户真实 key，gitignore）+ `apikey.txt.example`（模板，进仓库）
  - Import 策略：`name_XX` 格式支持 `from src.layers.queue_02 import QueueLayerApi` 标准语法
  - 文档补全：CODEX_ARCHITECTURE.md 新增 Import 策略章节，CODEX_RULES_GIT.md 修正仓库 URL，CLAUDE.md 开工流程补 venv/api-key 步骤，ONBOARD.md 新增开发环境设置和 apikey 说明
- 11 层目录结构 + README.md（骨架只读文档）
- 5 个 Skill 文件（coding/testing/debugging/refactor/review）
- `.gitignore` 覆盖：`.venv/`、`__pycache__/`、`apikey.txt`、`.local-secrets/`、IDE/OS 残留
