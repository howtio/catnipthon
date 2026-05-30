# 04 Harness — 运行编排层

## 一句话职责

管理一次 Agent Run 的完整生命周期：创建 runId → 调 Context → Skills → Memory → Runner → 验收 → final report。

## 文件结构

```
harness_04/
  __init__.py           — 导出 wrapper 和 types
  wrapper.py            — 本层唯一对外入口
  types.py              — 本层类型定义
  create_run.py         — run 创建
  run_lifecycle.py      — 生命周期管理
  max_step_policy.py    — 步数限制策略
  acceptance_check.py   — 验收检查
  build_final_report.py — final report 生成
  safe_git_diff.py      — 安全 git diff
```

## 依赖

- 05-context
- 06-skills
- 07-memory
- 08-runner
- 09-eventbus

## 允许

- 管理 run 生命周期
- 超时包装
- 运行限制配置
- 事件发布（run.started / run.finished / run.heartbeat）

## 禁止

- 不直接执行工具
- 不直接读写业务文件
- 不写复杂模型推理逻辑
