# ONBOARD：5 分钟速览

> 新会话、新 Codex 接手时的唯一入口。读完直接干活。

---

## 1. 我是谁

**catnip-agent** — Python 实现的本地 Coding Agent Runtime。

---

## 2. 架构

```text
01-gateway → 02-queue → 03-worker → 04-harness → 05-context → 06-skills → 07-memory → 08-runner → 09-eventbus → 10-tool-registry → 11-executor
   接单        排队        消费        管run        准备资料      提供方法      整理记忆      做决策       传事件        管工具定义       执行副作用
```

11 层（01~11），每层一个文件夹，一个 `wrapper.py` 对外，一个功能一个文件。

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

| 项目 | 状态 |
|------|------|
| 版本 | `0.0` |
| 代码 | 无（纯文档骨架） |
| typecheck | 未执行 |
| 测试 | 未执行 |

---

## 5. 版本规则

```
0.0  →  骨架搭建、文档体系、目录结构（当前）
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
| 了解某层职责边界 | `src/layers/XX-xxx/README.md` |

---

## 7. ⚠️ 开工强制清单

**以下每一步都必须完成。跳过 = 不允许写代码。**

```
□ 1. 读 ONBOARD.md
□ 2. 读 docs/DEV_PROGRESS.md
□ 3. git branch --show-current && git status
□ 4. 创建远端备份分支并 git push（备份命名见 CODEX_RULES_GIT.md）
□ 5. 记录备份分支名和提交号到 Session Contract
□ 6. 写 Session Contract（目标、涉及层、验收标准、非目标）
□ 7. mypy src/（确认起点干净）
```

**即使是同一会话连续开发下一步，也必须重新过一遍。**

---

## 8. ⚠️ 收尾强制清单

**以下每一步都必须完成。缺任何一步 = 本轮不算完成。**

```
□ 1. mypy src/（必须通过）
□ 2. pytest（或最小必要测试，必须通过）
□ 3. 更新 docs/LOG.md（写版本号！）
□ 4. 更新 docs/DEV_PROGRESS.md
□ 5. 更新 docs/LAYER_STATUS.md
□ 6. git add + git commit
□ 7. git push（！！！）
□ 8. 记录本次提交号
□ 9. 最终输出中说明：测试结果、push分支名、提交号、回滚判断
```

**没 push = 本轮不算完成。没更新日志 = 本轮不算完成。没写版本号 = 本轮不算完成。**

---

## 9. 环境变量速查

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
| `CATNIP_BROWSER_OPEN_BIN` | 浏览器打开命令 | `xdg-open` |

---

## 10. DeepSeek API Key 存放

```
catnipthon/
├── .local-secrets/          ← gitignore，不进仓库
│   └── deepseek.env         ← DEEPSEEK_API_KEY=sk-xxx
├── .env.example             ← 占位符，进仓库
```

## 11. 安全红线

- **绝对禁止**把真实 API Key 写进仓库的任何文件
- **绝对禁止**把密钥写进 git 历史
- 密钥只在 `.local-secrets/` 或环境变量
- 仓库只提交 `.env.example`（含占位符）
