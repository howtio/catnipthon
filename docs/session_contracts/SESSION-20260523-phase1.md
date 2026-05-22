# Session Contract / 2026-05-23

## 开工确认（逐项打勾）

- [x] 已读 `ONBOARD.md`
- [x] 已读 `docs/DEV_PROGRESS.md`
- [x] `git branch --show-current`: main
- [x] `git status`: clean
- [x] 远端备份已 push：分支 `backup/20260523-phase1-start` 提交 `9f5457f`
- [x] `mypy src/`: 通过（无 Python 文件，起点干净）

## 版本

`0.0` → `0.1`

## 目标

实现 Phase 1：Gateway + Queue + Worker 最小链路，打通 CLI 输入 → 任务创建 → 入队 → 消费。

## 涉及层

- [x] 01-gateway
- [x] 02-queue
- [x] 03-worker
- [ ] 04-harness（仅占位接口，不做实现）
- [ ] 05-context
- [ ] 06-skills
- [ ] 07-memory
- [ ] 08-runner
- [ ] 09-eventbus
- [ ] 10-tool-registry
- [ ] 11-executor
- [x] shared
- [x] tests

## 具体任务

- [ ] 创建 `src/shared/` — types、logger、errors、utils
- [ ] 创建 `src/bootstrap.py` — 依赖组装
- [ ] 创建 `src/main.py` — CLI 启动入口
- [ ] 实现 02-queue — 内存 FIFO、入队/出队、任务状态 pending/running/done/failed
- [ ] 实现 03-worker — 消费循环、调用 Harness 占位、错误捕获
- [ ] 实现 01-gateway — CLI 参数解析、创建 RunTask、提交 Queue、等待结果
- [ ] 编写 `tests/test_queue.py` 至少 2 个测试

## 验收标准

- [ ] `mypy src/` 通过
- [ ] `pytest` 通过
- [ ] 新增测试至少 2 个通过
- [ ] `python -m src.main "phase1 smoke test"` 能创建任务并入队出队
- [ ] `docs/LOG.md` 已追加记录（版本号 `0.1`）
- [ ] git push

## 非目标（明确不做）

- 不做 Harness 真实实现（占位即可）
- 不做 Context/Skills/Memory/Runner/EventBus/Tool Registry/Executor
- 不做 DeepSeek API 接入
- 不做 JSONL 日志
- 不做最终 report

## 风险预判

- Phase 1 涉及 shared 类型定义，需要一次性设计好基础类型避免后续大量返工

---

## 结果（Session 结束后填写）

- [ ] 目标达成 / [ ] 部分达成 / [ ] 未达成

| 检查项 | 结果 |
|--------|------|
| mypy | 通过 / 失败 |
| test | __ 通过 / __ 失败 |
| docs/LOG.md | 已更新 / 未更新 |
| docs/DEV_PROGRESS.md | 已更新 / 未更新 |
| docs/LAYER_STATUS.md | 已更新 / 未更新 |
| git commit | 提交号 ________ |
| git push | 已 push / 未 push（原因：____） |
| 回滚判断 | 需要 / 不需要 |

## 修改文件

- (Session 结束后填写)
