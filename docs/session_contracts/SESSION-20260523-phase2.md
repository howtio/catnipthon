# Session Contract / 2026-05-23 (Phase 2)

## 开工确认（逐项打勾）

- [x] 已读 `ONBOARD.md`
- [x] 已读 `docs/DEV_PROGRESS.md`
- [x] `git branch --show-current`: main
- [x] `git status`: clean
- [x] 远端备份已 push：分支 `backup/20260523-phase2-start` 提交 `260c662`
- [x] `mypy src/`: 通过（17 文件 0 问题）

## 版本

`0.1` → `0.2`

## 目标

实现 Phase 2：EventBus + Context + Skills + Memory + Harness 真实编排。

## 涉及层

- [x] 04-harness（替换占位为真实编排）
- [x] 05-context
- [x] 06-skills
- [x] 07-memory
- [x] 08-runner（仅占位接口）
- [x] 09-eventbus
- [x] shared（补充事件类型、记忆类型）
- [x] tests

## 具体任务

- [ ] 实现 09-eventbus — 事件发布订阅（publish/subscribe）
- [ ] 实现 05-context — 文档加载、workspace 扫描、system prompt 构建
- [ ] 实现 06-skills — 技能注册表、关键词匹配、SKILL.md 加载注入
- [ ] 实现 07-memory — MemorySnapshot、working memory、持久化
- [ ] 重构 04-harness — 串联 Context → Skills → Memory → Runner 占位 → final report
- [ ] 编写测试

## 验收标准

- [x] `mypy src/` 通过（28 文件 0 问题）
- [x] `pytest` 通过（38/38）
- [x] `python -m src.main "phase2 smoke test"` 输出 run 生命周期事件
- [x] `docs/LOG.md` 已追加记录（版本号 `0.2`）
- [x] git push（提交号 `5f64a02`）

## 非目标（明确不做）

- 不做 Runner 真实实现（占位即可）
- 不做 Tool Registry / Executor
- 不做 DeepSeek API 接入
- 不做 JSONL 日志

## 风险预判

- Harness 编排层涉及 5 个子层，需控制复杂度
- Memory 持久化格式需要一次性设计好
