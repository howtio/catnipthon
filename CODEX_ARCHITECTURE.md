# CODEX Architecture：分层契约与架构规则

> 本文档定义每一层的职责、接口、依赖、允许事项和禁止事项。
> 所有跨层开发必须遵守本文件的契约。

---

## 调用链

```text
Gateway → Queue → Worker → Harness → Context → Skills → Memory → Runner → EventBus → Tool Registry → Executor
```

上层只感知直接下层，不跨层调用：
- Gateway 只调 Queue
- Worker 只调 Queue + Harness
- Harness 只调 Context + Skills + Memory + Runner
- Runner 只调 EventBus
- Executor 监听 EventBus + 查询 Tool Registry

---

## 01 Gateway — 入口层

**职责：**
- 接收用户输入（CLI 参数、交互模式、stdin 管道）
- 校验用户输入
- 创建 RunTask
- 提交任务到 Queue
- 等待并展示任务结果

**依赖：** Queue

**允许：**
- 解析 CLI 参数
- 格式化输出
- 启动动画

**禁止：**
- 不调用模型
- 不执行工具
- 不读写 workspace
- 不直接调用 Executor
- 不直接调用 Runner

---

## 02 Queue — 队列层

**职责：**
- 任务入队
- 任务出队
- 维护任务状态：`pending → running → done / failed`
- 提供任务快照和完成等待
- 通知任务状态变化

**依赖：** 无

**允许：**
- 内存 FIFO 队列
- 任务状态查询
- 订阅任务变化

**禁止：**
- 不理解任务含义
- 不调用 Harness
- 不调用模型
- 不执行工具
- 不管理线程池（归属 Worker）

---

## 03 Worker — 消费层

**职责：**
- 从 Queue 消费任务
- 控制并发数量（workerCount）
- 生成和发送 Worker 心跳
- 调用 Harness 运行任务
- 捕获错误并标记任务 done/failed
- 回写运行结果到任务状态

**依赖：** Queue + Harness

**允许：**
- 线程池 / 并发消费槽
- Worker 心跳

**禁止：**
- 不构建 prompt
- 不直接调用模型
- 不直接执行工具

---

## 04 Harness — 运行编排层

**职责：**
- 创建 runId，管理一次 Agent Run 的完整生命周期
- 调用 Context 构建上下文
- 调用 Skills 注入技能说明
- 调用 Memory 读取记忆
- 调用 Runner 执行模型循环
- 调用 Memory 回写记忆
- 结束时执行验收检查
- 生成 final report
- 发布 run.started / run.heartbeat / run.finished
- 强制 git_diff（安全审计）
- Run 级超时控制

**依赖：** Context + Skills + Memory + Runner + EventBus

**允许：**
- 管理 run 生命周期
- 超时包装
- 运行限制配置

**禁止：**
- 不直接执行工具
- 不直接读写业务文件
- 不写复杂模型推理逻辑

---

## 05 Context — 上下文层

**职责：**
- 读取 docs 施工文档
- 扫描 workspace 摘要
- 加载 session history
- 提取开工强制清单
- 提取待续任务
- 构建 base system prompt
- 整理当前任务、权限、workspace、可用工具说明

**依赖：** 文件系统（只读）

**允许：**
- 读取文件
- 解析 Markdown
- 摘要生成

**禁止：**
- 不修改 workspace
- 不执行 shell
- 不调用模型

---

## 06 Skills — 技能层

**职责：**
- 根据用户任务选择相关 SKILL.md
- 读取技能说明文件
- 把技能说明注入 context

**关键原则：**
```
Skill 是说明书，不是真实工具。
Skill 负责告诉 Agent 什么时候做、怎么做、按什么流程做。
Tool 负责真实执行动作。
```

**依赖：** 文件系统（只读 skills/ 目录）

**允许：**
- 关键词匹配选择技能
- 加载 Markdown

**禁止：**
- Skills 层不执行文件读写
- Skills 层不执行 shell
- Skills 层不调用 Executor

---

## 07 Memory — 记忆层

**职责：**
- 维护 session 级短期记忆
- 维护结构化 working memory（工作对象追踪）
- 持久化 project memory 到本地文件
- 提取和注入记忆上下文
- 抽取工具结果中的工作对象
- 提供记忆清理能力
- 注入 startup checklist 和 carry-over tasks

**依赖：** 文件系统（读写 `logs/catnip-memory.json`）

**允许：**
- 读写记忆文件
- 按 sessionId 分桶
- 记忆裁剪（maxEntries）

**禁止：**
- 不读写 workspace 业务文件
- 不执行 shell
- 不直接调用模型
- 不接数据库、向量库或远程存储

---

## 08 Runner — 决策层

**职责：**
- 调用 AI SDK（DeepSeek 或 heuristic provider）
- 执行受控 ReAct Loop
- 让模型决定是否调用工具
- 把工具调用转换成 EventBus 事件
- 等待工具结果
- 把工具结果返回给模型
- 步数限制和工具失败重试
- 输出最终回答

**关键约束：**
```
Runner 不直接执行工具。
Runner 不直接读写文件。
Runner 不直接执行 shell。
Runner 只能通过 EventBus 发起 tool.call.requested。
```

**依赖：** EventBus + openai Python SDK（DeepSeek OpenAI 兼容接口）

**允许：**
- 调用 OpenAI-compatible chat completions API
- 管理 step 计数
- Provider 选择（deepseek / heuristic）

**禁止：**
- 不直接执行工具
- 不直接维护 session memory（委托给 Memory 层）
- 不绕过 Memory 自行缓存历史

---

## 09 EventBus — 事件层

**职责：**
- 传递 run.started / run.finished
- 传递 agent.step.finished
- 传递 tool.call.requested
- 传递 tool.call.result
- 传递 tool.call.failed
- 传递 worker.heartbeat / run.heartbeat
- 传递 prompt.composed / agent.plan.generated
- 提供 waitForToolResult
- 允许 Logger 旁路订阅所有事件

**依赖：** 无（Python asyncio.Event 或自定义事件系统）

**允许：**
- 事件发布订阅
- 事件过滤

**禁止：**
- MVP 不引入 Redis / Kafka / MQ

---

## 10 Tool Registry — 工具注册层

**职责：**
- 注册工具定义
- 解析工具名称
- 校验工具 schema
- 声明工具所需权限
- 返回工具 definition（给 AI SDK tools 参数）

**关键原则：**
```
Tool Registry 只说明"工具是什么"。
Executor 才负责"工具怎么执行"。
```

**依赖：** 无

**允许：**
- 管理工具元数据
- 按 category 筛选工具

**禁止：**
- 不直接读写文件
- 不执行 shell
- 不绕过 Executor

---

## 11 Executor — 执行层

**职责：**
- 监听 tool.call.requested
- 通过 Tool Registry 解析工具
- 执行 permissionGuard
- 执行 pathGuard
- 执行 commandGuard
- 真正执行工具
- 发布 tool.call.result 或 tool.call.failed
- 记录审计日志

**关键原则：**
```
Executor 是唯一副作用边界。
所有读文件、写文件、patch、shell 执行，只能发生在 Executor。
```

**依赖：** Tool Registry + EventBus + 文件系统 + subprocess

**允许：**
- 文件读写
- shell 命令执行（受 commandGuard 约束）
- 浏览器打开（受 pathGuard 约束）

**禁止：**
- 不做推理
- 不做任务规划

---

## 跨层 Import 规则

```
1. 每层只能通过 __init__.py 暴露 wrapper 和 types
2. 跨层调用只能 import 对方 __init__.py（或 from layer import wrapper）
3. 不允许跨层 import 对方内部功能文件
4. 不允许 Runner import Executor
5. 不允许 Runner import Tool implementation
6. 不允许 Skills import Executor
7. 不允许 Context 写文件或执行 shell
8. 不允许 Gateway 直接调用 Runner
9. 不允许 Worker 直接调用 Runner
10. Executor 是唯一允许产生副作用的层
```

---

## bootstrap.py 组装规则

所有层的依赖必须在 `src/bootstrap.py` 中组装。

组装顺序（从底层到上层）：

```text
EventBus → Tool Registry → Executor → Runner → Skills → Context → Memory → Harness → Queue → Worker → Gateway
```

禁止在某个层内部随意实例化其他层。

---

## wrapper.py 标准

每层必须有 `wrapper.py`，是该层唯一对外入口。

标准格式：

```python
def create_xxx_layer(deps: XxxLayerDeps) -> XxxLayerApi:
    return XxxLayerApi(
        # 注入依赖，暴露方法
    )

class XxxLayerApi:
    def some_action(self, input) -> Result:
        # 1. 校验输入
        # 2. 调用本层功能文件
        # 3. 调用下一层 wrapper
        # 4. 返回标准结果
        ...
```

`wrapper.py` 只负责组装依赖和转发调用，不堆积业务细节。
