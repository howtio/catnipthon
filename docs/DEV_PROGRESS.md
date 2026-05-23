# Development Progress

> 当前总进度快照。新会话接手时，本文件是第一个该读的进度文件。
> 详细施工记录见 `docs/LOG.md`。

---

## 当前版本

`0.0`（脚手架 3.0）

---

## 整体状态

| 项目 | 状态 |
|------|------|
| 版本 | `0.0` |
| 脚手架 1.0（基础文档 + 目录） | 已完成 |
| 脚手架 2.0（Python 工程化 + 导入策略） | 已完成 |
| 脚手架 3.0（马拉松接力 + 防漂移 + CLI开机动画） | 已完成 |
| Phase 1（Gateway + Queue + Worker） | 未开始（曾实现后在 3.0 重构中剥离） |
| Phase 2（Harness + Context + Skills + Memory） | 未开始（曾实现后在 3.0 重构中剥离） |
| Phase 2（Harness + Context + Skills + Memory） | 未开始 |
| Phase 3（Runner + EventBus 骨架） | 未开始 |
| Phase 4（Tool Registry + Executor 骨架） | 未开始 |
| Phase 5（最小工具集） | 未开始 |
| Phase 6（DeepSeek 接入 + tool calling） | 未开始 |
| Phase 7（日志、验收、final report） | 未开始 |
| typecheck | 通过（shared 组件） |
| 测试 | 暂无（纯脚手架） |

---

## 进行中

- 无（脚手架 3.0 就绪，等待首次代码施工）

---

## 未开始

- Phase 1 ~ 7

---

## 已完成

- 脚手架 1.0：项目文档体系（ONBOARD.md、CODEX_*.md、施工文档、进度追踪）
- 脚手架 2.0（2026-05-23）：
  - Python 工程化：`pyproject.toml`、`.venv/` 虚拟环境、mypy strict 模式、pytest 配置
  - 目录命名：层目录使用 `gateway_01`、`queue_02` 等（名称_数字，标准 Python import 可用）
  - API Key 管理：`apikey.txt`（用户真实 key，gitignore）+ `apikey.txt.example`（模板，进仓库）
  - Import 策略：`name_XX` 格式支持 `from src.layers.queue_02 import QueueLayerApi` 标准语法
- 脚手架 3.0（2026-05-23）：
  - 马拉松自动接力规则（CLAUDE.md）
  - 文档防漂移机制（版本号单一真相来源：pyproject.toml → version.py）
  - CLI 开机动画组件化（src/shared/cli.py，可复用）
  - CLI 风格文档（docs/CLI_STYLE.md）
  - 脚手架复用指南（ONBOARD.md §13）
  - 5 个 Skill 文件（coding/testing/debugging/refactor/review）
  - `.gitignore` 覆盖：`.venv/`、`__pycache__/`、`apikey.txt`、`.local-secrets/`、IDE/OS 残留
