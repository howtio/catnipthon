# Development Progress

> 当前总进度快照。新会话接手时，本文件是第一个该读的进度文件。
> 详细施工记录见 `docs/LOG.md`。

---

## 当前版本

`0.7`（Phase 7：日志、验收、final report）

---

## 整体状态

| 项目 | 状态 |
|------|------|
| 版本 | `0.7` |
| 脚手架 1.0（基础文档 + 目录） | 已完成 |
| 脚手架 2.0（Python 工程化 + 导入策略） | 已完成 |
| 脚手架 3.0（马拉松接力 + 防漂移 + CLI开机动画） | 已完成 |
| Windows 特化（路径/命令/配置 Windows 优先） | 已完成 |
| Phase 1（Gateway + Queue + Worker） | **已实现** ✅ |
| Phase 2（Harness + Context + Skills + Memory + EventBus） | **已实现** ✅ |
| Phase 3（Runner + EventBus + Tool Registry + Executor 骨架） | **已实现** ✅ |
| Phase 4（Tool Registry 完善 + Executor Guard 框架） | **已实现** ✅ |
| Phase 5（最小工具集） | **已实现** ✅ |
| Phase 6（DeepSeek 接入 + tool calling） | **已实现** ✅ |
| Phase 7（日志、验收、final report） | **已实现** ✅ |
| typecheck | 通过（91 文件，0 错误） |
| 测试 | 60 个，全部通过 |

---

## 进行中

- Phase 6（DeepSeek 接入 + tool calling）

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
- Windows 特化（2026-05-23）：
  - 路径分隔符统一使用 Windows 风格（`\`），文档同时保留 Unix 写法
  - `.venv\Scripts\` 作为首要虚拟环境路径
  - API Key 加载新增 PowerShell 命令
  - 浏览器默认命令设为 `start`（Windows）
  - CLAUDE.md / ONBOARD.md 全面同步 Windows 优先指令
