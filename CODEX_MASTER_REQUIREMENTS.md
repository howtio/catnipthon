# Catnip Agent 总工程指令

> 本文件是项目最高优先级文档。
> 新 Codex 接手必须先读 `ONBOARD.md`，再读本文件。
> 本文件是"宪法"——只定原则和指向，具体规则在专题文档中。

---

## 1. 项目目标

项目名：`catnip-agent`

构建一个本地运行、可控、可扩展、可观测的 Coding Agent Runtime。

核心学习目标：
1. Agent Runtime 分层设计
2. Gateway / Queue / Worker 任务流
3. Harness 运行编排
4. Context 构建与 Memory 记忆管理
5. Skills 与 Tools 分离
6. Runner 受控 ReAct Loop
7. EventBus 工具事件解耦
8. Tool Registry 工具注册
9. Executor 副作用边界
10. JSONL 日志与施工日志记录

---

## 2. 11 层架构

```text
Gateway → Queue → Worker → Harness → Context → Skills → Memory → Runner → EventBus → Tool Registry → Executor
```

| 层 | 一句话职责 | 详细 |
|----|-----------|------|
| 01-gateway | 接单：接收输入、校验、创建任务、提交队列 | `CODEX_ARCHITECTURE.md` |
| 02-queue | 排队：FIFO 入队出队、任务状态维护 | `CODEX_ARCHITECTURE.md` |
| 03-worker | 消费：拉取任务、控制并发、调用 Harness | `CODEX_ARCHITECTURE.md` |
| 04-harness | 管 run：生命周期、验收、final report | `CODEX_ARCHITECTURE.md` |
| 05-context | 准备资料：读文档、扫描 workspace、构建 system prompt | `CODEX_ARCHITECTURE.md` |
| 06-skills | 提供方法：选择技能说明并注入上下文 | `CODEX_ARCHITECTURE.md` |
| 07-memory | 整理记忆：session 短期记忆 + 持久化 project memory | `CODEX_ARCHITECTURE.md` |
| 08-runner | 做决策：ReAct Loop、调用 AI SDK、决策工具调用 | `CODEX_ARCHITECTURE.md` |
| 09-eventbus | 传事件：所有 run/step/tool 事件传递和日志旁路 | `CODEX_ARCHITECTURE.md` |
| 10-tool-registry | 管工具定义：注册、schema、权限声明 | `CODEX_ARCHITECTURE.md` |
| 11-executor | 执行副作用：guard 检查、工具执行、审计日志 | `CODEX_ARCHITECTURE.md` |

---

## 3. 四个铁律

```
Skills 不执行        — Skill 是说明书，告诉 Agent 怎么做，不自己动手
Tools 不决策         — Tool 是工具箱，只负责执行，不判断什么时候该用
Runner 不碰副作用    — Runner 只能通过 EventBus 发起 tool.call.requested
Executor 不做推理    — Executor 只做 guard → 执行 → 返回结果
```

---

## 4. 当前产品边界

当前只做本地 CLI Agent MVP。

**当前禁止：** WebUI、Electron、Docker sandbox、Redis、数据库、多 Agent、外部长期记忆、远程部署、PyPI publish

---

## 5. 调用链与 Import 规则

### 标准调用顺序

```text
Gateway → Queue → Worker → Harness → Context → Skills → Memory → Runner → EventBus → Tool Registry → Executor
```

### Import 规则

1. 每层只能通过 `__init__.py` 暴露 `wrapper` 和 `types`
2. 跨层调用只能 import 对方 `__init__.py`
3. 不允许跨层 import 对方内部功能文件
4. 不允许 Runner import Executor
5. 不允许 Runner import Tool implementation
6. 不允许 Skills import Executor
7. 不允许 Context 写文件或执行 shell
8. 不允许 Gateway 直接调用 Runner
9. 不允许 Worker 直接调用 Runner
10. Executor 是唯一允许产生副作用的层

---

## 6. 线程池与心跳归属

| 能力 | 归属层 | 说明 |
|------|--------|------|
| 线程池/并发消费 | 03-worker | Queue 只存任务，Worker 管调度 |
| Worker 心跳 | 03-worker | 标记存活、忙闲、队列深度 |
| Run 心跳 | 04-harness | 感知 run 是否长时间无进展 |
| 心跳事件传播 | 09-eventbus | 发布 worker.heartbeat / run.heartbeat |

---

## 7. 模型接入原则

- DeepSeek 只接到 `08-runner`
- 不允许把模型逻辑散落到其他层
- Context、Skills、Memory、Harness、Executor 必须保持模型无关
- API Key 只能通过环境变量注入，**绝对禁止**写入仓库

---

## 8. 施工阶段总计划

| Phase | 内容 | 版本 | 状态 |
|-------|------|------|------|
| Phase 0 | 目录、文档、进度体系 | 0.0 | 已完成 |
| Phase 1 | Gateway + Queue + Worker 骨架 | 0.1 | 未开始 |
| Phase 2 | Harness + Context + Skills + Memory + EventBus 基础 | 0.2 | 未开始 |
| Phase 3 | Runner + EventBus 工具回调 | 0.3 | 未开始 |
| Phase 4 | Tool Registry + Executor 骨架 | 0.4 | 未开始 |
| Phase 5 | 最小工具集 (list_files/read_file/write_file/patch_file/shell_exec/git_diff) | 0.5 | 未开始 |
| Phase 6 | DeepSeek 接入 + AI SDK tool calling | 0.6 | 未开始 |
| Phase 7 | 日志、验收、final report | 0.7 | 未开始 |
| MVP | 全链路可跑、通过验收任务 | **1.0** | 未开始 |
| 扩展 | 浏览器工具、搜索工具、Memory 持久化、CLI 增强 | 1.x | 未开始 |

---

## 9. 版本体系

```
0.0 → 0.1 → 0.2 → ... → 0.7 → 1.0 (MVP)
                                ↓
                         用户检查后宣布
                        2.0 → 2.1 → ...
                                ↓
                         用户检查后宣布
                              3.0 ...
```

规则：
- `0.0` 到 `1.0` 按 Phase 自动推进
- 每次 `docs/LOG.md` 条目必须写版本号
- **1.0 之后的大版本号（2.0、3.0）由用户在检查时拍板，不允许自行跨越**
- Git tag 格式：`v0.0`、`v0.1`、...、`v1.0`、`v2.0`

---

## 10. ⚠️ 开发流程（不可跳过）

### 每次开工前

```
读 ONBOARD.md + DEV_PROGRESS.md
  → git status
    → 远端备份分支 + git push
      → 写 Session Contract
        → 开始写代码
```

### 每次收尾

```
typecheck + test
  → 更新 LOG.md（写版本号！）+ DEV_PROGRESS.md + LAYER_STATUS.md
    → git commit
      → git push（！！！）
        → 记录提交号 + 最终说明
```

**详细规则见 `CODEX_RULES_GIT.md` 和 `CODEX_RULES_TESTING.md`。**

---

## 11. 文档体系

```
ONBOARD.md                          ← 5 分钟速览，新会话唯一入口
CODEX_MASTER_REQUIREMENTS.md        ← 本文件，宪法
CODEX_ARCHITECTURE.md               ← 分层契约、import 规则、副作用边界
CODEX_RULES_GIT.md                  ← Git 协作、备份、回滚规则
CODEX_RULES_TESTING.md              ← 测试标准、分阶段测试
CODEX_SESSION_CONTRACT_TEMPLATE.md  ← 马拉松 Session 契约模板
docs/DEV_PROGRESS.md                ← 当前进度、待续任务
docs/LOG.md                         ← 施工日志（索引 + 最近条目）
docs/LAYER_STATUS.md                ← 11 层实现状态一览
src/layers/xxx_XX/README.md         ← 每层职责、允许/禁止、依赖
```
