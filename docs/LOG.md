# Construction Log

> 施工日志。按版本归档到 `docs/logs/`。
> 本文件只保留索引 + 最近 3 条记录。

---

## 日志归档

| 版本 | 文件 |
|------|------|
| 0.0 | `docs/logs/LOG-0.0.md` |
| 0.1 | `docs/logs/LOG-0.0.md`（已剥离） |
| 0.2 | `docs/logs/LOG-0.0.md`（已剥离） |

---

## 日志模板

```markdown
## YYYY-MM-DD / Phase X / 标题

### 版本
- `0.x`

### 目标
本次施工目标。

### 开工检查
- 当前分支、备份分支名、备份提交号

### 本次修改
- 修改点 1

### 改动部分
- 模块：做了什么

### 修改文件
- file1

### 验证结果
- mypy src/：通过 / 失败
- pytest：通过 / 失败
- 冒烟测试：通过 / 未执行

### 回滚判断
- 是否发生需要回滚的错误
- 如需回滚，回滚目标提交号

### 风险
- 风险 1

### 下一步
下一步计划。
```

---

## 最近记录

### 2026-05-23 / Windows 特化 — catnipthon 全面 Windows 优先适配

- **版本**: `0.0`（Windows 特化脚手架 3.0）
- **改动部分**:
  - 文档修复：README 版本号修正、11 层 README 目录名修正、LOG 归档、Phase 回滚历史标注
  - Windows 特化：路径改为 Windows 优先（`\`）、`.venv\Scripts\` 首要路径、PowerShell API Key 加载
  - 浏览器默认命令设为 `start`（Windows）
  - CLAUDE.md / ONBOARD.md / 各文档全面同步 Windows 优先指令
  - 主线仓库标注：`https://github.com/howtio/catnipthon`
- **修改文件**: 21 个文档文件修复 + 5 个文件 Windows 特化
- **验证**: mypy 通过（shared 组件）
- **下一步**: Phase 1 — Gateway + Queue + Worker

### 2026-05-23 / 脚手架 3.0 — 马拉松接力 + 防漂移 + CLI开机动画组件化

- **版本**: `0.0`（脚手架 3.0）
- **改动部分**:
  - 剥离所有 Phase 1/2 实现代码，回归纯脚手架状态
  - CLI 开机动画组件化：`src/shared/cli.py`（TITLE/SUBTITLE/LAYERS 可覆盖）
  - 版本管理：`src/shared/version.py`（pyproject.toml 单一真相源）
  - 马拉松自动接力规则：CLAUDE.md 新增最高优先级规则
  - 文档防漂移机制：收尾流程新增版本同步 + 漂移检查步骤
  - CLI 风格文档：`docs/CLI_STYLE.md`
  - ONBOARD.md：架构图命名修正 + §13 脚手架复用指南
  - 层 __init__.py 清空为占位符，bootstrap.py/main.py 简化为脚手架模板
  - 删除所有测试文件和 Session Contract（纯脚手架不需要）
- **修改文件**: 删除 17 个实现文件，重写 5 个文档 + bootstrap/main
- **验证**: mypy 通过（shared 组件），CLI 开机动画正常
- **下一步**: 基于脚手架 3.0 重新开始 Phase 1 施工

### 2026-05-23 / Phase 2 / Harness + Context + Skills + Memory + EventBus

- **版本**: `0.2`
- **改动部分**:
  - `09-eventbus` — 异步 pub/sub 事件系统（publish/subscribe/unsubscribe），事件类型常量
  - `05-context` — 文档加载（ONBOARD/CLAUDE/ARCHITECTURE）、workspace 扫描、system prompt 构建、开工清单提取
  - `06-skills` — 技能注册表、关键词匹配（5 个技能 × 多关键词）、SKILL.md 加载、默认 fallback 到 coding
  - `07-memory` — MemorySnapshot（session/working/carryover）、JSON 持久化、裁剪（max 50 session / 20 obs / 10 files）、记忆注入 prompt
  - `04-harness` — 真实编排替换占位：Context → Skills → Memory → Runner → EventBus → final report
  - `08-runner` — Phase 2 占位（返回 mock answer + 上下文长度）
  - 新增测试：eventbus 5 个、context 5 个、skills 8 个、memory 8 个、harness 3 个
- **修改文件**: src/layers/{eventbus_09,context_05,skills_06,memory_07,harness_04,runner_08}/*, src/bootstrap.py, tests/*
- **验证**: mypy 通过（28 文件 0 问题），pytest 38/38 通过，冒烟测试通过（事件发布、文档加载 16199 chars、技能匹配 "testing"、final report 生成）
- **下一步**: Phase 3 — Runner + EventBus 完善（tool.call.requested/result 路由）
