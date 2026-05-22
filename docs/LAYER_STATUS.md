# Layer Status：11 层实现状态一览

> 某一层有开发动作时，只需更新对应段落。
> 本文件替代原来的 11 个独立分层进度日志。

---

## 01 Gateway

**状态**: 未开始（仅 README）

**待实现:**
- CLI 参数解析
- 用户输入校验
- RunTask 创建
- 任务提交到 Queue
- 结果展示

---

## 02 Queue

**状态**: 未开始（仅 README）

**待实现:**
- 内存 FIFO 队列
- 入队/出队
- 任务状态管理（pending → running → done / failed）
- 任务快照和完成等待

---

## 03 Worker

**状态**: 未开始（仅 README）

**待实现:**
- Worker 消费循环
- 并发控制
- Worker 心跳
- 错误处理与捕获

---

## 04 Harness

**状态**: 未开始（仅 README）

**待实现:**
- runId 创建
- run 生命周期管理
- 调用链串联（Context → Skills → Memory → Runner）
- final report 生成
- 验收检查

---

## 05 Context

**状态**: 未开始（仅 README）

**待实现:**
- docs 文档读取
- workspace 扫描与摘要
- system prompt 构建
- 开工清单提取

---

## 06 Skills

**状态**: 未开始（仅 README）

**待实现:**
- 技能注册表
- 关键词匹配选择
- SKILL.md 文件加载
- 技能说明注入

---

## 07 Memory

**状态**: 未开始（仅 README）

**待实现:**
- session 级短期记忆
- 结构化 working memory
- 持久化 project memory
- 记忆注入与回写

---

## 08 Runner

**状态**: 未开始（仅 README）

**待实现:**
- ReAct Loop
- Provider 抽象（heuristic + DeepSeek）
- AI SDK 集成
- 步数限制与重试

---

## 09 EventBus

**状态**: 未开始（仅 README）

**待实现:**
- 事件发布订阅
- 工具调用事件传递
- waitForToolResult
- Logger 旁路订阅

---

## 10 Tool Registry

**状态**: 未开始（仅 README）

**待实现:**
- 工具定义注册
- 工具 schema 声明
- 工具解析接口
- 权限等级声明

---

## 11 Executor

**状态**: 未开始（仅 README）

**待实现:**
- 工具调用监听
- permissionGuard
- pathGuard
- commandGuard
- 工具执行
- 审计日志

---

## Shared

**状态**: 未开始

**待实现:**
- types: runTask、permission、tool、event、result
- logger: JSONL 日志、控制台日志
- errors: CatnipError、PolicyError、ToolError、TimeoutError
- utils: sleep、createId、safeJson、assertNever
