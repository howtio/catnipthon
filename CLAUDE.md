# Catnipthon — Claude Code 自动加载规则

> 本文件由 Claude Code 在每次会话启动时自动读取并注入系统提示。
> 不需要用户手动提醒，Claude Code 看到本文件就会遵守。

---

## 马拉松自动接力（最高优先级）

**这是最重要的规则。违反 = 马拉松失败。**

1. 完成一个 Phase 的收尾流程（commit + push + docs 更新）后，**立即自动开始下一 Phase**
2. **不需要等用户说"下一步"、"继续"、"开始"** — 用户已经授权你跑完全程
3. 自动读取 `docs/CONSTRUCTION_PLAN.md` 获取下一 Phase 的完整任务清单
4. 自动执行开工流程的步骤 1-8，然后开始写代码
5. 唯一停止条件：
   - 用户明确说 **"停"** / **"stop"** / **"暂停"** / **"halt"**
   - 所有 Phase（0-7）全部完成，到达 **1.0 MVP**
   - 遇到**无法自动解决**的阻塞（如 Phase 6 需要真实 API Key 但 apikey.txt 为空）
6. 如果在某个 Phase 中途被中断，恢复时从该 Phase 继续
7. 每个 Phase 完成后输出简洁的阶段性总结（≤10 行），然后直接开工下一 Phase
8. **绝对不要问"要我继续吗？"、"要开始下一阶段吗？"之类的问题**

---

## 项目身份

catnip-agent — Python 实现的 11 层 Coding Agent Runtime。
当前版本：见 `docs/DEV_PROGRESS.md`（以该文件为准）。
目标：1.0 MVP。

---

## 每次开工强制流程

**以下步骤必须逐项完成，不允许跳过。**

1. 激活虚拟环境：`.venv\Scripts\python --version`（Windows）或 `.venv/bin/python --version`（Linux/macOS）确认可用
2. 读 `ONBOARD.md`
3. 读 `docs/DEV_PROGRESS.md`（知道做到哪了）
4. `git branch --show-current && git status`
5. 创建远端备份分支并 push：`backup/<YYYYMMDD>-<phaseN>`
6. 加载 API Key：`export $(grep DEEPSEEK_API_KEY apikey.txt | xargs)`（Git Bash/Linux/macOS）或 PowerShell `Get-Content apikey.txt | ForEach-Object { $k,$v = $_ -split '='; if ($k -eq 'DEEPSEEK_API_KEY') { Set-Item -Path "env:$k" -Value $v } }`（Phase 6 起需要）
7. 填写 Session Contract（参考 `CODEX_SESSION_CONTRACT_TEMPLATE.md`）：目标、涉及层、验收标准、非目标
8. `mypy src/`（确认起点干净）

**没做完以上 8 步 = 不允许写代码。**

---

## CLI 输出风格（catnip 品牌）

所有 CLI 输出必须遵循 catnip 风格：

```
╔══════════════════════════════════════════════╗
║            catnip agent v0.x                ║
║    11-layer Coding Agent Runtime            ║
╚══════════════════════════════════════════════╝
```

- 使用 Unicode 框线字符（╔ ╗ ╚ ╝ ║ ═），不用 emoji
- 版本号从 `pyproject.toml` 动态读取
- 完成后输出 runId、steps、duration、状态
- 错误信息格式：`[!] 具体错误描述`

---

## 每次收尾强制流程

**以下步骤必须逐项完成，缺一不可。**

1. `mypy src/` — 必须通过
2. `pytest` — 必须通过
3. 更新 `docs/LOG.md`（写版本号 `0.x`）
4. 更新 `docs/DEV_PROGRESS.md`
5. 更新 `docs/LAYER_STATUS.md`
6. `pyproject.toml` 版本号与实际版本同步
7. `git add <具体文件>` + `git commit`
8. `git push`
9. 记录本次提交号和备份分支名
10. 输出总结（测试结果、提交号、回滚判断）

**没 push = 不算完成。没更新日志 = 不算完成。**

---

## 文档防漂移（每次收尾必须执行）

版本号是文档漂移的头号元凶。以下机制确保单一真相来源：

**真相源**：`pyproject.toml` 的 `version` 字段是唯一权威版本号。

**引用链**：
```
pyproject.toml (唯一真相源)
  └─ src/shared/version.py (运行时解析，自动同步)
       └─ src/shared/cli.py (CLI 开机动画版本)
```

**收尾时必须检查的漂移点**（缺一不可）：

| 文件 | 检查项 | 操作 |
|------|--------|------|
| `pyproject.toml` | `version = "0.x"` | 更新到当前版本 |
| `docs/DEV_PROGRESS.md` | 状态表版本号 | 更新到当前版本 |
| `ONBOARD.md` | §4 当前状态表 | 更新 typecheck/测试 数据 |
| `docs/LAYER_STATUS.md` | 涉及层的状态 | 更新已实现/待实现 |

**ONBOARD.md 特殊的防漂移设计**：§4 状态表不硬编码版本号，写"见 pyproject.toml（当前 ≈ 0.x）"。

**CI 检查点**（待实现）：`mypy src/ && pytest` 作为 pre-commit hook。

---

## 架构铁律

```
gateway_01 → queue_02 → worker_03 → harness_04 → context_05 → skills_06 → memory_07 → runner_08 → eventbus_09 → tool_registry_10 → executor_11

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
|
> Windows 用户：如果 `.venv\Scripts\python` 找不到模块，确保已激活虚拟环境（`.venv\Scripts\activate`）|

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
| CLI风格（脚手架） | `docs/CLI_STYLE.md` |

---

## 安全红线

- 绝对禁止把真实 API Key 写入仓库
- 密钥只在 `.local-secrets/` 或环境变量
- 仓库只提交 `.env.example`
