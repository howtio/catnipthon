# ONBOARD：5 分钟速览

> 新会话、新 Codex 接手时的唯一入口。读完直接干活。

---

## 1. 我是谁

**catnip-agent** — Python 实现的本地 Coding Agent Runtime。

---

## 2. 架构

```text
gateway_01 → queue_02 → worker_03 → harness_04 → context_05 → skills_06 → memory_07 → runner_08 → eventbus_09 → tool_registry_10 → executor_11
   接单        排队        消费        管run        准备资料      提供方法      整理记忆      做决策       传事件        管工具定义       执行副作用
```

11 层（名称_数字命名），每层一个文件夹，`wrapper.py` 对外，`__init__.py` 暴露接口。
Python import 示例：`from src.layers.queue_02 import QueueLayerApi`

---

## 3. 四个铁律

```
Skills 不执行        — 说明书
Tools 不决策         — 工具箱
Runner 不碰副作用    — 只通过 EventBus 发 tool.call.requested
Executor 不做推理    — 只做 guard → 执行 → 返回结果
```

---

## 4. 当前状态

> 精确版本号见 `pyproject.toml` 的 `version` 字段（单一真相来源）。
> 详细进度见 `docs/DEV_PROGRESS.md`。

| 项目 | 状态 |
|------|------|
| 版本 | 见 `pyproject.toml`（脚手架 3.0，代码 0.0） |
| 代码 | 纯脚手架，11 层待实现 |
| typecheck | mypy strict 模式，shared 组件通过 |
| 测试 | 暂无（纯脚手架） |

---

## 5. 版本规则

```
0.0  →  脚手架 3.0（文档体系 + 工程化 + CLI动画）← 当前
0.1  →  Phase 1 完成（Gateway + Queue + Worker）
0.2  →  Phase 2 完成（Harness + Context + Skills + Memory）
0.3  →  Phase 3 完成（Runner + EventBus 骨架）
0.4  →  Phase 4 完成（Tool Registry + Executor 骨架）
0.5  →  Phase 5 完成（最小工具集可用）
0.6  →  Phase 6 完成（DeepSeek 接入 + tool calling）
0.7  →  Phase 7 完成（日志、验收、final report）
1.0  →  MVP（全链路可跑、通过验收任务）
------ 以上按 Phase 自动推进，以下是用户拍板 ------
2.0  →  用户检查后宣布
3.0  →  用户检查后宣布
```

每次 `docs/LOG.md` 条目必须写版本号。未经用户明确确认，不允许跨大版本。

---

## 6. 文档索引

| 我要做什么 | 读哪个 |
|------------|--------|
| 快速了解项目 | `ONBOARD.md`（本文件） |
| 查最高原则和 Phase 计划 | `CODEX_MASTER_REQUIREMENTS.md` |
| 查架构和层契约 | `CODEX_ARCHITECTURE.md` |
| 查 Git 上传/备份/回滚 | `CODEX_RULES_GIT.md` |
| 查测试标准 | `CODEX_RULES_TESTING.md` |
| 开始一个开发 Session | `CODEX_SESSION_CONTRACT_TEMPLATE.md` |
| 看完整施工路线图 | `docs/CONSTRUCTION_PLAN.md` |
| 看 Agent 循环定义 | `docs/AGENT_LOOP.md` |
| 看工具权限和策略 | `docs/TOOL_POLICY.md` |
| 看分阶段调试指南 | `docs/DEBUG_GUIDE.md` |
| 看当前进度 | `docs/DEV_PROGRESS.md` |
| 看施工记录 | `docs/LOG.md` |
| 看每层实现状态 | `docs/LAYER_STATUS.md` |
| 了解某层职责边界 | `src/layers/xxx_XX/README.md` |
| CLI 开机动画复用 | `docs/CLI_STYLE.md` |

---

## 7. ⚠️ 开工强制清单

**以下每一步都必须完成。跳过 = 不允许写代码。**

```
□ 0. 激活虚拟环境：`.venv\Scripts\python --version`（Windows）或 `.venv/bin/python --version`（Linux/macOS）确认
□ 1. 读 ONBOARD.md
□ 2. 读 docs/DEV_PROGRESS.md
□ 3. git branch --show-current && git status
□ 4. 创建远端备份分支并 push：backup/<YYYYMMDD>-<phaseN>
□ 5. 加载 API Key（Phase 6 起需要）
□ 6. 写 Session Contract（目标、涉及层、验收标准、非目标）
□ 7. mypy src/（确认起点干净）
```

**即使是同一会话，马拉松模式会自动接力下一 Phase，但也必须重新过开工清单。**

> 马拉松规则见 `CLAUDE.md`：你不喊停，我就不停。

---

## 8. ⚠️ 收尾强制清单

**以下每一步都必须完成。缺任何一步 = 本轮不算完成。**

```
□ 1. mypy src/（必须通过）
□ 2. pytest（必须通过）
□ 3. 更新 docs/LOG.md（写版本号！）
□ 4. 更新 docs/DEV_PROGRESS.md
□ 5. 更新 docs/LAYER_STATUS.md
□ 6. 同步 pyproject.toml 版本号
□ 7. git add <具体文件> + git commit
□ 8. git push（！！！）
□ 9. 记录提交号 + 备份分支名
□ 10. 输出总结：测试结果、分支、提交号、回滚判断
```

**没 push = 不算完成。没更新日志 = 不算完成。版本号不一致 = 不算完成。**

---

## 9. 开发环境设置

```bash
# 创建虚拟环境（仅首次）
python -m venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate
# 或（Linux/macOS）
# source .venv/bin/activate

# 安装开发依赖（Windows）
.venv\Scripts\pip install mypy pytest pytest-asyncio openai
# 或（Linux/macOS）
# .venv/bin/pip install mypy pytest pytest-asyncio openai
```

虚拟环境 `.venv/` 已在 `.gitignore` 中排除，不进仓库。

---

## 10. 环境变量速查

| 变量 | 作用 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek 密钥 | 无 |
| `CATNIP_RUNNER_PROVIDER` | 模型 provider | `heuristic` |
| `CATNIP_RUNNER_MAX_STEPS` | 最大步数 | `10` |
| `CATNIP_RUNNER_MAX_TOOL_RETRIES` | 工具失败重试次数 | `2` |
| `CATNIP_RUNNER_CONTINUE_ON_TOOL_ERROR` | 工具失败后继续执行 | `false` |
| `CATNIP_RUN_TIMEOUT_MS` | run 超时（毫秒） | `180000` |
| `CATNIP_WORKER_COUNT` | Worker 并发数 | `1` |
| `CATNIP_WORKER_HEARTBEAT_MS` | Worker 心跳间隔 | `5000` |
| `CATNIP_MEMORY_STORAGE_FILE` | 记忆持久化路径 | `logs/catnip-memory.json` |
| `CATNIP_BROWSER_OPEN_BIN` | 浏览器打开命令 | `start`（Windows） / `xdg-open`（Linux/macOS） |

---

## 11. DeepSeek API Key 存放

```
catnipthon/
├── apikey.txt                ← gitignore，不进仓库（推荐）
├── apikey.txt.example        ← 模板文件，进仓库
├── .local-secrets/           ← gitignore，不进仓库
│   └── deepseek.env          ← DEEPSEEK_API_KEY=sk-xxx
├── .env.example              ← 占位符，进仓库
```

加载方式：
- **Git Bash / Linux/macOS**: `export $(grep DEEPSEEK_API_KEY apikey.txt | xargs)`
- **PowerShell**: `Get-Content apikey.txt | ForEach-Object { $k,$v = $_ -split '='; if ($k -eq 'DEEPSEEK_API_KEY') { Set-Item -Path "env:$k" -Value $v } }`
- **cmd.exe**: 暂不支持，建议用 PowerShell 或 Git Bash

---

## 12. 安全红线

- **绝对禁止**把真实 API Key 写进仓库的任何文件
- **绝对禁止**把密钥写进 git 历史
- 密钥只在 `.local-secrets/` 或环境变量
- 仓库只提交 `.env.example`（含占位符）

---

## 13. 脚手架复用：把 catnip 当模板用（★ 给脚手架用户）

**想基于 catnip 脚手架开新项目？按下面来：**

### 最小复用（只拿 CLI 动画）

```python
# 1. 复制 src/shared/cli.py + version.py 到你的项目
# 2. 在你的 main.py 中：
from src.shared.cli import print_header, print_task_bar, print_result_ok

print_header()       # 开机动画（自动读 pyproject.toml 版本）
print_task_bar(msg)  # 任务分隔线
print_result_ok(id, result)  # 成功输出
```

详细文档：`docs/CLI_STYLE.md`

### 完整复用（基于整套脚手架开发）

```
1. git clone <catnipthon> my-agent
2. 修改 pyproject.toml：name、version
3. 修改 src/shared/cli.py：TITLE、SUBTITLE、LAYERS
4. 删除不需要的层目录
5. 开始开发你自己的层
```

### 脚手架提供什么

| 组件 | 路径 | 说明 |
|------|------|------|
| CLI 开机动画 | `src/shared/cli.py` | 可覆盖 TITLE/SUBTITLE/LAYERS |
| 版本管理 | `src/shared/version.py` | 自动读 pyproject.toml |
| 基础类型 | `src/shared/types.py` | RunTask、TaskStatus |
| 错误体系 | `src/shared/errors.py` | CatnipError 五子类 |
| 日志工具 | `src/shared/logger.py` | get_logger |
| 11 层架构 | `src/layers/` | 每层 README + __init__ 模板 |
| 开发文档 | `docs/` + `CODEX_*` | 完整施工体系 |

### 不提供什么

- 不绑定任何特定模型（DeepSeek / OpenAI 等）
- 不绑定任何特定工具集
- 不绑定任何特定部署方式

- **绝对禁止**把真实 API Key 写进仓库的任何文件
- **绝对禁止**把密钥写进 git 历史
- 密钥只在 `.local-secrets/` 或环境变量
- 仓库只提交 `.env.example`（含占位符）
