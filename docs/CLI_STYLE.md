# Catnip CLI Style Guide

> 任何基于 catnip 脚手架的项目自动获得本风格。
> 本文件是风格参考，不是实现代码。实现见 `src/shared/cli.py`。

---

## 开机动画

运行 `python -m src.main` 时自动打印：

```
╔══════════════════════════════════════════════╗
║                                              ║
║           catnip agent  v0.2                 ║
║       11-Layer Coding Agent Runtime          ║
║                                              ║
╠══════════════════════════════════════════════╣
║                  Layers                      ║
╠══════════════════════════════════════════════╣
║   gateway_01  →  queue_02    →  worker_03    ║
║   harness_04  →  context_05  →  skills_06    ║
║   memory_07   →  runner_08   →  eventbus_09  ║
║       tool_registry_10 → executor_11         ║
╚══════════════════════════════════════════════╝
```

版本号从 `pyproject.toml` 自动读取，永不硬编码。

---

## 如何在你的项目中使用

### 1. 直接使用（零配置）

```python
from src.shared.cli import print_header, print_task_bar, print_result_ok

print_header()
print_task_bar("your task description")
# ... run your task ...
print_result_ok(task_id, result_text)
```

### 2. 自定义品牌

在你的 `main.py` 中覆盖标题常量：

```python
from src.shared import cli

cli.TITLE = "my-agent"
cli.SUBTITLE = "My Custom Agent Runtime"

# 或者重写 BANNER 字符串
cli.BANNER = """...your custom banner..."""
```

### 3. 完全自定义

直接复制 `src/shared/cli.py` 到你的项目，修改 `TITLE`、`SUBTITLE`、`LAYERS` 常量。

---

## 输出格式规范

| 类型 | 格式 | 用途 |
|------|------|------|
| 成功 | `[OK]` | 任务完成 |
| 失败 | `[!]` | 任务失败 |
| 分隔线 | `─` × 46 | 区块分隔 |
| 框线 | `╔ ╗ ╚ ╝ ║ ═ ╠ ╣` | 品牌头部 |

**禁止使用 emoji。** 只用 Unicode 框线字符。

---

## 版本管理（防漂移）

- **单一真相来源**: `pyproject.toml` → `version = "0.x"`
- **运行时读取**: `src/shared/version.py` 解析 `pyproject.toml`
- **所有模块引用**: `from src.shared import VERSION`（永不硬编码版本号）
- **CLI 自动同步**: `src/shared/cli.py` 通过 `version.py` 读取版本
- **文档不写死版本号**: 文档用"当前版本见 `pyproject.toml`"代替硬编码数字

每次 Phase 完成后更新 `pyproject.toml` 的 `version` 字段，所有引用处自动跟随。

---

## 与脚手架的关系

```
新项目用 catnip 脚手架初始化
        │
        ▼
src/shared/cli.py  ← 自动获得开机动画
src/shared/version.py ← 自动获得版本管理
src/main.py ← 自动获得 catnip 风格 CLI
        │
        ▼
只需改 TITLE / SUBTITLE / LAYERS 即可定制品牌
```
