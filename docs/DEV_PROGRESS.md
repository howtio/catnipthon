# Development Progress

> 当前总进度快照。新会话接手时，本文件是第一个该读的进度文件。
> 详细施工记录见 `docs/LOG.md`。

---

## 当前版本

`7.0`（Web UI v1 — 情书 Agent 完整发布）

## 当前施工中

**支线：** `给阿嬷的agent`
**当前阶段：** Web UI v1 — 已完成

### 本阶段已完成（全部）
- `.venv/` 虚拟环境创建 + 依赖安装
- git 仓库初始化 + 首次提交 `af0b20c` + GitHub 推送
- 备份分支：`backup/20260530-initial`、`backup/20260530-webui-v1-start`、`backup/20260530-webui-v1-final`
- 施工文档体系更新（CONSTRUCTION_PLAN / CODEX_MASTER / DEV_PROGRESS）
- `mypy src` 通过（96 文件），`pytest` 通过（75/75）
- CSS 低高度布局极紧压缩（max-height: 720px 新增 30+ 规则）
- `/api/chat` 真实 agent 联调验证（heuristic + DeepSeek 双 provider 全链路可跑）
- webui_server.py 增加异常处理（500 错误返回 JSON，而非挂起请求）
- 定位 curl/bash 传中文 JSON 时 Content-Length 差异问题（前端浏览器 fetch 正常）
- 会话持久化（localStorage 存储，刷新不丢数据）
- PDF 自动导出（html2pdf.js 实现，点击即自动下载，无打印弹窗）
- PDF 文件名按创建时间自动命名：`情书-{YYYYMMDD-HHmmss}.pdf`
- PDF 样式与 Web UI 信纸完全一致（vertical-rl 竖排书法风格）
- 实时思考显示（后台线程 + EventBus 订阅 + 前端轮询，回信未封缄时显示 agent 推理过程）
- 信纸加载中的字体和排版与写信/发信完全一致
- Google Fonts 非阻塞加载（media="print" + onload 策略，解决国内卡死问题）
- 清空信匣功能（确认弹窗 + 清空 localStorage + 清除服务端记忆）
- 旧信匣对话历史独立翻看弹窗 + 每条可单独 PDF 导出
- 实时写完 startup guide + 提交 + push GitHub

### 待完成（Web UI v2 — 可选的下一阶段）
- [ ] 低高度窗口木棉花/纸飞机浏览器目测验收
- [ ] 移动端适配验证（手机真机或模拟器）
- [ ] 流式输出接入前端（SSE / WebSocket）

---

## 整体状态

| 项目 | 状态 |
|------|------|
| 版本 | `7.0` |
| 脚手架 1.0（基础文档 + 目录） | 已完成 |
| 脚手架 2.0（Python 工程化 + 导入策略） | 已完成 |
| 脚手架 3.0（马拉松接力 + 防漂移 + CLI开机动画） | 已完成 |
| Windows 特化（路径/命令/配置 Windows 优先） | 已完成 |
| Phase 1（Gateway + Queue + Worker） | **已实现** ✅ |
| Phase 2（Harness + Context + Skills + Memory + EventBus） | **已实现** ✅ |
| Phase 3（Runner + EventBus + Tool Registry + Executor 骨架） | **已实现** ✅ |
| Phase 4（Tool Registry 完善 + Executor Guard 框架） | **已实现** ✅ |
| Phase 5（最小工具集） | **已实现** ✅ |
| Phase 6（DeepSeek 接入 + tool calling） | **已实现** ✅ |
| Phase 7（日志、验收、final report） | **已实现** ✅ |
| 1.0 MVP | **已实现** 🏆 |
| CLI 2.0（交互式 REPL + 实时进度） | **已实现** ✅ |
| v4.0 工具增强（web_fetch, web_search, open_browser, file_search） | **已实现** ✅ |
| 会话记忆（SessionMemory，进程内跟踪） | **已实现** ✅ |
| Token 优化（紧凑描述、历史压缩、结果截断） | **已实现** ✅ |
| URL 安全守卫（SSRF 防护） | **已实现** ✅ |
| v5.0 防卡死（流式超时 60s） | **已实现** ✅ |
| v5.0 Web 搜索增强（duckduckgo_search + BeautifulSoup） | **已实现** ✅ |
| v5.0 open_browser 结果引导 + max_steps 提升 | **已实现** ✅ |
| v7.0 搜索增强（ddgs 迁移 + HTTP 后备） | **已实现** ✅ |
| v7.0 CLI 交互大修（思考过滤 + 流式答案 + 警告抑制） | **已实现** ✅ |
| v7.0 System Prompt 优化（shell_exec 约束） | **已实现** ✅ |
| Web UI v1（情书 Agent 完整发布） | ✅ 已完成 |
| Web UI v2（流式输出 + 历史持久化） | 📋 待开始 |
| Web UI v3（完整能力替代 CLI REPL） | 📋 待开始 |
| typecheck | 通过（96 文件，0 错误） |
| 测试 | 75 个，全部通过 |

---

## 已完成

- 脚手架 1.0：项目文档体系（ONBOARD.md、CODEX_*.md、施工文档、进度追踪）
- 脚手架 2.0（2026-05-23）：
  - Python 工程化：`pyproject.toml`、`.venv/` 虚拟环境、mypy strict 模式、pytest 配置
  - 目录命名：层目录使用 `gateway_01`、`queue_02` 等（名称_数字，标准 Python import 可用）
  - API Key 管理：`apikey.txt`（用户真实 key，gitignore）+ `apikey.txt.example`（模板，进仓库）
  - Import 策略：`name_XX` 格式支持 `from src.layers.queue_02 import QueueLayerApi` 标准语法
- 脚手架 3.0（2026-05-23）：
  - 马拉松自动接力规则（CLAUDE.md）
  - 文档防漂移机制（版本号单一真相来源：pyproject.toml → version.py）
  - CLI 开机动画组件化（src/shared/cli.py，可复用）
  - CLI 风格文档（docs/CLI_STYLE.md）
  - 脚手架复用指南（ONBOARD.md §13）
  - 5 个 Skill 文件（coding/testing/debugging/refactor/review）
  - `.gitignore` 覆盖：`.venv/`、`__pycache__/`、`apikey.txt`、`.local-secrets/`、IDE/OS 残留
- Windows 特化（2026-05-23）：
  - 路径分隔符统一使用 Windows 风格（`\`），文档同时保留 Unix 写法
  - `.venv\Scripts\` 作为首要虚拟环境路径
  - API Key 加载新增 PowerShell 命令
  - 浏览器默认命令设为 `start`（Windows）
  - CLAUDE.md / ONBOARD.md 全面同步 Windows 优先指令
- v4.0 工具增强（2026-05-24）：
  - 切换模型：`deepseek-reasoner` → `deepseek-chat`（修复工具调用卡死 + 大幅减少 token 消耗）
  - 新增 4 个工具：`web_fetch`（httpx 抓取）、`web_search`（DuckDuckGo HTML 搜索）、`open_browser`（浏览器打开）、`file_search`（名称/内容搜索）
  - 工具总量：6 MVP → 10 个
  - 新增 `web` 工具分类（ToolCategory）
  - URL Guard：SSRF 防护（拦截 localhost/私有 IP）
  - 工具描述全面压缩（30-50% 更短）
- 会话记忆 + Token 优化（2026-05-24）：
  - `SessionMemory`：进程内会话跟踪（文件读写、工具调用、用户备注）
  - 历史压缩：`_compress_history()` 旧 tool 结果截断为 500 字符
  - 结果截断：`_truncate()` 工具结果限制 2000 字符
  - Session 上下文自动注入 system prompt
- v5.0 防卡死 + Web 增强（2026-05-24）：
  - 流式超时 60s：`client.chat.completions.create(timeout=60)`，流停滞抛 APITimeout
  - web_search 改用 `duckduckgo_search.DDGS` 库（取代脆弱 HTML 正则）
  - _fetch_url 改用 `BeautifulSoup` 解析（正确移除 script/style，干净文本）
  - open_browser 引导 agent 继续：消息追加 "Continue with the next step."
  - max_steps 10→20（默认），15→20（run_lifecycle）
  - httpx / beautifulsoup4 / duckduckgo-search 正式加入 pyproject.toml
- v7.0 搜索增强（2026-05-24）：
  - `duckduckgo_search` → `ddgs` 迁移，消除 RuntimeWarning
  - 新增 `_search_ddg_html()` HTTP 后备搜索（httpx + BeautifulSoup 直抓 DDG）
  - 双后备策略：ddgs 库为主，HTTP 直搜为后备
- v7.0 CLI 交互大修（2026-05-24）：
  - `print_thinking()` 过滤无意义碎片，只显示真实推理
  - 新增 `print_streaming_answer()` 最终答案流式显示
  - 新增 `AGENT_ANSWER_CHUNK` 事件类型
  - `warnings.filterwarnings("ignore")` 抑制包警告
  - System Prompt 约束 shell_exec 使用范围
- Web UI v1 完整发布（2026-05-30）：
  - 新增仓库内前端目录 `webui/`，保留页面代码与 GUI 素材
  - 新增 `src/shared/webui_server.py`，提供静态页面托管与 `/api/chat`
  - `src/main.py` 新增 `--webui` 启动入口
  - `webui/app.js` 现在优先走 HTTP API，`file://` 场景保留 mock
  - 新增 `tests/test_webui_server.py` 覆盖结果提取与历史格式转换
  - localStorage 会话持久化（刷新不丢数据）
  - PDF 自动导出（html2pdf.js，一键下载无弹窗）
  - 实时 agent 思考显示（EventBus → 后台线程 → 前端轮询）
  - 清空信匣功能（前端 localStorage + 服务端记忆同步清除）
  - Google Fonts 非阻塞加载（解决国内卡死问题）
  - 最终校验：`mypy src` 通过（96 文件），`pytest` 通过（75/75）
  - git commit + push + 备份分支 + startup guide
