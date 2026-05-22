# Agent Loop

> 定义 Catnip Agent 的完整运行循环。
> Runner 和 Harness 的实现以本文件为蓝图。

---

## 完整流程（15 步）

```text
1.  Gateway 接收用户输入，校验，创建 RunTask
2.  Queue 任务入队，状态 = pending
3.  Worker 从 Queue 拉取任务，状态 → running
4.  Harness 创建 runId，发布 run.started
5.  Context 读取施工文档、扫描 workspace、构建 system prompt
6.  Skills 根据任务选择并加载 SKILL.md，注入方法说明
7.  Memory 读取 session 记忆 + working memory，注入上下文
8.  Runner 调用模型（DeepSeek / heuristic），进入 ReAct Loop
9.  Runner 决策 → 通过 EventBus 发布 tool.call.requested
10. EventBus 路由工具请求到 Executor
11. Executor → Tool Registry 解析工具定义 → permissionGuard → pathGuard → commandGuard → 执行
12. EventBus 将 tool.call.result 或 tool.call.failed 返回 Runner
13. Runner 继续 ReAct Loop 直到 step 上限或模型输出最终回答
14. Memory 回写本次 run 的工具摘要和最终结果
15. Harness 强制 git_diff，生成 final report，发布 run.finished
```

---

## Runner 约束

- 不直接执行工具
- 不直接读写文件
- 不直接执行 shell
- 只能通过 EventBus 发起 `tool.call.requested`
- 不自己拼接和持久化记忆（委托 Memory 层）

---

## Memory 约束

- 先做 session/run 级短期记忆
- 先做受控摘要，不把全部历史原样塞给 Runner
- 记忆写入由 Memory 层统一收口
- 持久化到 `logs/catnip-memory.json`

---

## Step 控制

- 最大 step 数：`CATNIP_RUNNER_MAX_STEPS`（默认 10）
- 每 step 记录 usage
- 每 step 记录 tool call
- 工具失败重试：`CATNIP_RUNNER_MAX_TOOL_RETRIES`（默认 2）
- run 级超时：`CATNIP_RUN_TIMEOUT_MS`（默认 180000）

---

## 模型接入

- DeepSeek 接在 `08-runner` 的 provider adapter 层
- 通过 openai Python SDK（DeepSeek 兼容接口）
- Context、Skills、Memory、Harness、Executor 保持模型无关
