# Debugging Skill

## When to use

当用户要求定位 bug、排查故障、分析错误日志时使用。

## Process

1. 先明确故障现象和复现步骤
2. 读相关日志文件（logs/catnip.jsonl、logs/catnip-trace.jsonl）
3. 定位到具体层和文件
4. 用 read_file 查看可疑代码
5. 确认根因后再提出修复方案
6. 修复后复测验证
7. 输出根因、修复内容、验证结果

## Recommended tools

- list_files
- read_file
- shell_exec
- git_diff

## Forbidden behavior

- 不允许未定位根因就修改代码
- 不允许修改不相关的文件
- 不允许忽略错误日志
