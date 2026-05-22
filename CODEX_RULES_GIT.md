# CODEX Rules：Git 协作、备份与回滚

> **GitHub 上传不是"建议"，是每一轮开发的硬门槛。**
> 核心原则：先备份再开发；完成即上传；出问题回滚上一版本。

---

## ⚠️ 开工前（每次写代码前必做）

以下每一步都必须完成。**跳过 = 不允许写代码。**

### 第一步：读文档

```bash
# 读 ONBOARD.md（必读）
# 读 docs/DEV_PROGRESS.md（必读）
```

### 第二步：检查 Git 状态

```bash
git branch --show-current
git status
```

确认：
- 当前分支是什么
- 有没有未提交的改动
- 工作区是否干净

### 第三步：创建远端备份（硬门槛）

```bash
# 备份分支命名：backup/<YYYYMMDD>-<描述>
git checkout -b backup/20260523-phase1-start
git push -u origin backup/20260523-phase1-start

# 切回开发分支
git checkout main
```

**必须 push 到 GitHub。必须记录备份分支名和提交号。**

没有远端备份 = 不允许写代码。

### 第四步：写 Session Contract

```
目标、涉及层、验收标准、非目标
```

### 第五步：确认起点干净

```bash
mypy src/
```

---

## ⚠️ 收尾（每次写完代码必做）

以下每一步都必须完成。**缺任何一步 = 本轮不算完成。**

### 第一步：测试

```bash
mypy src/            # 必须通过
pytest               # 或最小必要测试，必须通过
```

### 第二步：更新文档

```bash
# 更新 docs/LOG.md（写版本号！）
# 更新 docs/DEV_PROGRESS.md
# 更新 docs/LAYER_STATUS.md
```

### 第三步：提交

```bash
git add <具体文件>    # 不允 git add -A 或 git add .
git commit -m "..."   # 提交信息需包含改动目的、范围、测试结果
```

### 第四步：推送

```bash
git push
```

**没 push = 本轮不算完成。不许说"已完成但没 push"。**

### 第五步：输出总结

在最终回复中必须包含：

```
- 测试结果
- Push 分支名和提交号
- 开发前备份分支名和提交号
- 回滚判断结果
- 本轮测试命令
```

---

## 分支策略

| 改动类型 | 分支策略 |
|----------|----------|
| 文档改动 | 可在用户明确同意时直推 `main` |
| 代码改动 | 创建功能分支，如 `feat/phase-1-queue-worker` |
| 结构性重构 | 不得直推 `main` |

---

## 备份命名规范

```
backup/<YYYYMMDD>-<简短描述>
```

示例：
- `backup/20260523-pre-phase1`
- `backup/20260523-before-tool-implementation`

---

## 提交信息规范

```text
<type>: <简短描述>

版本：0.x

改动部分：
- <模块>：<做了什么>

测试：<测试结果>

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 回滚规则

### 触发回滚的情况

- 测试明显退化
- 修复成本高于本轮收益
- 变更污染了不相关层
- 架构边界被破坏

### 回滚顺序（从轻到重）

1. 文件级回滚（只撤销具体文件）
2. 提交级回滚（回到本轮前的提交）
3. 分支级回滚（回到备份分支）

**默认优先最小范围回滚。**

### 回滚后必须做

```
1. git status
2. mypy src/ + pytest
3. 更新 docs/LOG.md（记录回滚原因）
4. 最终输出说明：回滚了什么、为什么、复测结果、复测命令
```

---

## 版本命名

```
开发阶段版本：
  0.0 → 0.1 → 0.2 → ... → 0.7 → 1.0 (MVP)

Git tag：
  v0.0, v0.1, v0.2, ... v1.0, v2.0, v3.0

大版本号（整数位）：
  1.0 MVP
  2.0+ 由用户在检查时宣布，不允许自行跨越
```

---

## GitHub 仓库信息

| 项目 | 值 |
|------|-----|
| 仓库地址 | `https://github.com/howtio/catnipmvp.git` |
| SSH | `git@github.com:howtio/catnipmvp.git` |
| 默认分支 | `main` |
| Remote | `origin` |
