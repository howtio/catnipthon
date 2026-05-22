# 06 Skills — 技能层

## 一句话职责

根据用户任务选择相关 SKILL.md，把技能说明注入上下文。

## 关键原则

```
Skill 是说明书，不是真实工具。
Skill 负责告诉 Agent 怎么做、按什么流程做。
Tool 负责真实执行动作。
```

## 文件结构

```
06-skills/
  __init__.py           — 导出 wrapper 和 types
  wrapper.py            — 本层唯一对外入口
  types.py              — 本层类型定义
  skill_registry.py     — 技能注册表
  select_skills.py      — 技能选择
  load_skill_markdown.py — 技能文件加载
  inject_skills.py      — 技能注入
  skill_matcher.py      — 关键词匹配
```

## 依赖

- 文件系统（只读 skills/ 目录）

## 允许

- 关键词匹配选择技能
- 加载 Markdown 技能文件

## 禁止

- 不执行文件读写
- 不执行 shell
- 不调用 Executor
