# Refactor Skill

## When to use

当用户要求重构代码、改善结构、提取公共逻辑、优化架构时使用。

## Process

1. 先理解当前代码结构和依赖关系
2. 确认重构范围和目标架构
3. 确保不破坏现有测试
4. 小步修改，每步验证
5. 检查跨层 import 是否仍然合规
6. 修改后跑完整测试集
7. 输出重构摘要、影响范围、风险

## Recommended tools

- list_files
- read_file
- write_file
- patch_file
- shell_exec
- git_diff

## Forbidden behavior

- 不允许破坏分层架构边界
- 不允许修改层契约
- 不允许跳过测试验证
- 不允许未读依赖方代码就修改接口
