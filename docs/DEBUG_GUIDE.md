# Debug Guide

> 开发各阶段的调试目标和可检查项。

---

## 文档阶段（Phase 0 / 0.0）

- 目录是否完整（11 层 + docs + skills + logs + workspaces + tests）
- `docs/` 关键文档是否齐全
- `skills/` 5 个 SKILL.md 是否齐全
- `logs/` 与 `workspaces/demo/` 是否存在
- 架构说明是否和 CODEX_MASTER_REQUIREMENTS 一致

---

## 骨架阶段（Phase 1-4 / 0.1-0.4）

- `mypy src/` 必须通过
- `__init__.py` 导出关系是否可解析
- 不允许循环 import
- 每层 wrapper 是否正确组装依赖

---

## 工具阶段（Phase 5 / 0.5）

### 单工具调试

```bash
# 用 pytest 测单个工具模块
pytest tests/test_tools.py -v -k "list_files"
```

- 先测单个工具（list_files、read_file）
- 再测写入工具（write_file、patch_file）
- 再测 shell_exec（白名单命令）
- 最后测 git_diff

### Guard 调试

- permissionGuard：低权限任务能否拦截高权限工具
- pathGuard：workspace 外路径能否被拦截
- commandGuard：危险命令（rm、sudo）能否被拦截

---

## 模型阶段（Phase 6 / 0.6）

### Provider 调试

- 无 key 时是否返回明确错误
- heuristic provider 是否正常 fallback
- DeepSeek provider 单轮调用是否成功

### Tool Calling 调试

- 模型是否正确发起 tool.call.requested
- EventBus 是否正确传递 tool.call.result
- 多步工具调用是否按 ReAct Loop 正常流转

### 日志调试

- `logs/catnip.jsonl` 是否有事件记录
- `logs/catnip-trace.jsonl` 是否有 prompt/plan/reasoning
- `run.report` 是否包含 stepsUsed、finalAnswer、toolSummaryCount

---

## 端到端阶段（Phase 7 / 0.7）

### 冒烟测试

```bash
python -m src.main "readme and git diff"
python -m src.main "create file workspaces/demo/hello.html with a complete html page"
```

### 验收任务

```bash
python -m src.main "在 workspace/demo 中创建 src/add.py，实现 add(a, b) 函数，创建测试文件，运行测试，输出修改摘要"
```

### 验收标准

- `logs/catnip.jsonl` 记录完整工具调用链路
- CLI 输出包含 runId、steps、toolSummaryCount、finalAnswer
- `docs/LOG.md` 已追加工记录
