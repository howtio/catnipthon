# 07 Memory — 记忆层

## 一句话职责

维护 session 短期记忆 + 结构化 working memory + 持久化 project memory。

## 架构位置

```
Context → Skills → Memory → Runner
```

在 Skills 注入方法说明之后，Runner 做决策之前，Memory 把最近工作上下文注入 system prompt。

## 文件结构

```
07-memory/
  __init__.py  — 导出 wrapper 和 types
  wrapper.py   — 本层唯一对外入口
  types.py     — 本层类型定义
```

## 依赖

- 文件系统（读写 `logs/catnip-memory.json`）

## 核心数据结构

```
MemorySnapshot {
  sessionEntries[]      — session 级短期记忆
  workingSet            — 当前工作对象
    focusedFilePath     — 焦点文件
    focusedOpenableHtmlPath — 焦点 HTML
    recentFilePaths[]   — 最近文件
    openableHtmlPaths[] — 可打开 HTML
  observations[]        — 工具结果抽取
  projectRecentEntries[] — 持久化记忆
  carryoverTasks[]      — 待续任务
  startupChecklist[]    — 开工清单
}
```

## 允许

- 读写记忆文件
- 从工具结果抽取工作对象
- 记忆裁剪

## 禁止

- 不读写 workspace 业务文件
- 不执行 shell
- 不直接调用模型
- 不接数据库、向量库或远程存储
