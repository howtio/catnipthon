# Tool Policy

> 定义所有工具的权限等级、路径策略、命令策略。
> Executor 的 guard 实现以本文件为唯一依据。

---

## 范围说明

**MVP (1.0) 工具：** list_files、read_file、write_file、patch_file、shell_exec、git_diff

**1.x 扩展工具（不在 MVP 范围）：** open_browser、web_search、open_browser_search、open_url
以下权限表中扩展工具的规则仅供后续参考，当前不实现。

---

## 权限等级

### low

允许：
- `list_files`
- `read_file`

拒绝：
- `write_file`
- `patch_file`
- `shell_exec`
- `open_browser`
- `web_search`
- `open_browser_search`
- `open_url`

### medium

允许：
- `list_files`
- `read_file`
- `write_file`
- `patch_file`
- `git_diff`
- `open_browser`
- `web_search`
- `open_browser_search`
- `open_url`

受限允许 (shell_exec 仅白名单命令)：
- `pytest`
- `pytest tests/`
- `python -m pytest`
- `pip install`
- `git status`
- `git diff`
- `ls`
- `cat`

浏览器预览限制：
- `open_browser` 仅允许打开 `workspaces/demo/` 下的 `.html/.htm` 文件
- 不允许直接打开 workspace 任意文件
- 不允许借此执行任意 shell 命令

搜索工具限制：
- `web_search` 仅允许传入文本查询词和受限 `limit`
- `open_browser_search` 仅允许把查询词交给默认搜索引擎打开
- `open_url` 仅允许打开 `http/https` 绝对链接

### high

允许：
- `medium` 全部能力

后续可扩展：
- `pip install`（任意包）

---

## 始终禁止

- `rm`
- `rm -rf`
- `sudo`
- `chmod`
- `chown`
- `curl`
- `wget`
- `ssh`
- `scp`
- `git push`
- `pip publish` / `twine upload`
- `docker`
- `powershell`

---

## 路径策略

- 仅允许访问 workspace 内路径
- 所有路径操作必须经过 pathGuard
- 不允许越过项目根目录
- `open_browser` 仅允许 `workspaces/demo/*.html`

---

## 命令策略

- 所有 shell 命令必须经过 commandGuard
- 不允许执行危险命令
- 不允许拼接不透明动态命令
- shell_exec 在 medium 权限下仅允许白名单命令
