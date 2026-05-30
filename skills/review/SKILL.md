# Review Skill

## When to use

当用户要求审查代码、检查架构合规性、审计安全边界时使用。

## Process

1. 先用 git_diff 查看改动范围
2. 逐文件检查是否遵守层契约
3. 检查 import 是否有跨层违规
4. 检查副作用是否只发生在 Executor
5. 检查 guard 是否覆盖了所有新工具路径
6. 检查测试是否覆盖了改动
7. 输出审查结论、违规项、建议

## Recommended tools

- git_diff
- read_file
- list_files
- shell_exec

## Forbidden behavior

- 不允许只看 diff 不看上下文
- 不允许忽略架构违规
- 不允许跳过 guard 审计
