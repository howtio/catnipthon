# Catnipthon — Claude Code 自动加载规则

> 本文件由 Claude Code 在每次会话启动时自动读取并注入系统提示。
> 不需要用户手动提醒，Claude Code 看到本文件就会遵守。

---

## 项目身份

catnip-agent — Python 实现的 11 层 Coding Agent Runtime。
当前版本：0.0。目标：1.0 MVP。

---

## 每次开工强制流程

**以下步骤必须逐项完成，不允许跳过。**

1. 读 `ONBOARD.md`
2. 读 `docs/DEV_PROGRESS.md`（知道做到哪了）
3. `git branch --show-current && git status`
4. 创建远端备份分支并 push：`backup/<YYYYMMDD>-<描述>`
5. 填写 Session Contract（参考 `CODEX_SESSION_CONTRACT_TEMPLATE.md`）：目标、涉及层、验收标准、非目标
6. `mypy src/`（确认起点干净）

**没做完以上 6 步 = 不允许写代码。**

---

## 每次收尾强制流程

**以下步骤必须逐项完成，缺一不可。**

1. `mypy src/` — 必须通过
2. `pytest` — 必须通过
3. 更新 `docs/LOG.md`（写版本号 `0.x`）
4. 更新 `docs/DEV_PROGRESS.md`
5. 更新 `docs/LAYER_STATUS.md`
6. `git add <具体文件>` + `git commit`
7. `git push`
8. 记录本次提交号和备份分支名
9. 最终输出：测试结果、push 分支/提交号、回滚判断

**没 push = 不算完成。没更新日志 = 不算完成。**

---

## 架构铁律

```
01-gateway → 02-queue → 03-worker → 04-harness → 05-context → 06-skills → 07-memory → 08-runner → 09-eventbus → 10-tool-registry → 11-executor

Skills 不执行 — 说明书
Tools 不决策 — 工具箱
Runner 不碰副作用 — 只通过 EventBus 发起 tool.call.requested
Executor 不做推理 — 只做 guard → 执行 → 返回结果
```

---

## Import 规则

- 每层只能通过 `__init__.py` 暴露 wrapper 和 types
- 跨层调用只能 import 对方 `__init__.py`
- 不允许跨层 import 对方内部功能文件
- 不允许 Runner import Executor
- 不允许 Skills import Executor
- 不允许 Context 写文件或执行 shell
- 11-executor 是唯一副作用边界

---

## 测试命令

| 命令 | 用途 |
|------|------|
| `mypy src/` | 类型检查 |
| `pytest` | 运行全部测试 |
| `pytest tests/ -v` | 详细模式 |
| `python -m src.main "..."` | 冒烟测试 |

---

## 文档索引

| 需求 | 文件 |
|------|------|
| 5分钟速览 | `ONBOARD.md` |
| 宪法 | `CODEX_MASTER_REQUIREMENTS.md` |
| 层契约 | `CODEX_ARCHITECTURE.md` |
| Git规则 | `CODEX_RULES_GIT.md` |
| 测试规则 | `CODEX_RULES_TESTING.md` |
| 施工路线 | `docs/CONSTRUCTION_PLAN.md` |
| Agent循环 | `docs/AGENT_LOOP.md` |
| 工具策略 | `docs/TOOL_POLICY.md` |
| 调试指南 | `docs/DEBUG_GUIDE.md` |
| 当前进度 | `docs/DEV_PROGRESS.md` |
| 施工日志 | `docs/LOG.md` |
| 层状态 | `docs/LAYER_STATUS.md` |
| Session契约 | `CODEX_SESSION_CONTRACT_TEMPLATE.md` |

---

## 安全红线

- 绝对禁止把真实 API Key 写入仓库
- 密钥只在 `.local-secrets/` 或环境变量
- 仓库只提交 `.env.example`
