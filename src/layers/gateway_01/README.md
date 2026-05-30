# 01 Gateway — 入口层

## 一句话职责

接收用户输入，创建任务，提交队列，展示结果。

## 文件结构

```
gateway_01/
  __init__.py          — 导出 wrapper 和 types
  wrapper.py           — 本层唯一对外入口
  types.py             — 本层类型定义
  cli_gateway.py       — CLI 参数解析
  parse_cli_args.py    — 参数解析器
  create_run_task.py   — 任务创建
  validate_user_input.py — 输入校验
```

## 依赖

- 02-queue

## 允许

- 解析 CLI 参数
- 格式化终端输出
- 启动动画
- 交互模式 readline

## 禁止

- 不调用模型
- 不执行工具
- 不读写 workspace
- 不直接调用 Runner 或 Executor
