# Development Progress

> 当前总进度快照。新会话接手时，本文件是第一个该读的进度文件。
> 详细施工记录见 `docs/LOG.md`。

---

## 当前版本

`0.0`（骨架 2.0）

---

## 整体状态

| 项目 | 状态 |
|------|------|
| 版本 | `0.0` |
| Phase 0（骨架 1.0：基础文档 + 目录） | 已完成 |
| Phase 0（骨架 2.0：Python 工程化 + 导入策略） | 已完成 |
| Phase 1（Gateway + Queue + Worker） | 未开始 |
| Phase 2（Harness + Context + Skills + Memory） | 未开始 |
| Phase 3（Runner + EventBus 骨架） | 未开始 |
| Phase 4（Tool Registry + Executor 骨架） | 未开始 |
| Phase 5（最小工具集） | 未开始 |
| Phase 6（DeepSeek 接入 + tool calling） | 未开始 |
| Phase 7（日志、验收、final report） | 未开始 |
| typecheck | 未执行 |
| 测试 | 未执行 |

---

## 进行中

- 无（骨架 2.0 已完成，等待首次代码施工）

---

## 未开始

- Phase 1：Gateway + Queue + Worker 最小链路
- Phase 2 ~ 7

---

## 已完成

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
