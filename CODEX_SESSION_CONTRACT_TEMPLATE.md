# CODEX Session Contract Template

> 每次开发 Session 开始前复制本模板填入内容。
> Session 结束后补填"结果"部分，作为 `docs/LOG.md` 条目来源。

---

## Session Contract / YYYY-MM-DD

### 开工确认（逐项打勾）

- [ ] 已读 `ONBOARD.md`
- [ ] 已读 `docs/DEV_PROGRESS.md`
- [ ] `git branch --show-current`: ________
- [ ] `git status`: clean / dirty
- [ ] 远端备份已 push：分支 `________` 提交 `________`
- [ ] `mypy src/`: 通过 / 未执行

### 版本

`0.x`

### 目标

<!-- 一句话 -->

### 涉及层

- [ ] 01-gateway
- [ ] 02-queue
- [ ] 03-worker
- [ ] 04-harness
- [ ] 05-context
- [ ] 06-skills
- [ ] 07-memory
- [ ] 08-runner
- [ ] 09-eventbus
- [ ] 10-tool-registry
- [ ] 11-executor
- [ ] shared
- [ ] tests

### 具体任务

- [ ] 任务 1
- [ ] 任务 2
- [ ] 任务 3

### 验收标准

- [ ] `mypy src/` 通过
- [ ] `pytest` 通过
- [ ] 新增测试 __ 个，全部通过
- [ ] 冒烟通过：`<命令>`

### 非目标（明确不做）

- 不做 XXX
- 不改 YYY

### 风险预判

- 风险 1

---

### 结果（Session 结束后填写）

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

### 修改文件

- file1
- file2
