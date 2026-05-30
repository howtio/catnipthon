# Development Progress

> 当前总进度快照。新会话接手时，本文件是第一个该读的进度文件。
> 详细施工记录见 `docs/LOG.md`。

---

## 当前版本

`7.0`（Web UI v1 — 情书 Agent 接入完成）

## 当前施工中

**支线：** `给阿嬷的agent`
**当前阶段：** Web UI v1 — 接入完成，已验证

### 本阶段已完成
- `.venv/` 虚拟环境创建 + 依赖安装
- git 仓库初始化 + 首次提交 `af0b20c` + GitHub 推送
- 备份分支：`backup/20260530-initial`、`backup/20260530-webui-v1-start`、`backup/20260530-webui-v1-continue`
- 施工文档体系更新（CONSTRUCTION_PLAN / CODEX_MASTER / DEV_PROGRESS）
- `mypy src` 通过（96 文件），`pytest` 通过（75/75）
- Web UI 静态资源已整理到 `webui/`
- `src/main.py --webui` 启动入口可用
- `src/shared/webui_server.py` 提供静态托管、`/api/chat`、`/api/chat/think/:run_id`
- 前端 HTTP 协议已对齐异步 `run_id + poll` 模式
- 修复 Web UI 多轮中的“当前问题重复进入 history”
- 修复 Harness 每次 run 的 steps / tool_summary / token_usage 被历史累计的问题
- 修复 Windows `shell_exec` / `git_diff` 的解码 warning
- 收紧窄窗断点：`827 × 698` 下木槿花与纸飞机已完整可见
- Web UI 协议级冒烟通过：`POST /api/chat` → `GET /api/chat/think/:run_id` 可完成一轮问答

### 下一阶段（可选）
- [ ] 移动端适配与真机验收
- [ ] 把推理过程从轮询升级为真正流式输出（SSE / WebSocket）
- [ ] 继续优化回信中的过程文案，而不是直接展示工具痕迹

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
| Web UI v1（情书 Agent 接入 + 验证） | ✅ 已完成 |
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
- Web UI v1 接入完成（2026-05-30）：
  - 新增仓库内前端目录 `webui/`，保留页面代码与 GUI 素材
  - 新增 `src/shared/webui_server.py`，提供静态页面托管、异步问答桥接与轮询端点
  - `src/main.py` 新增 `--webui` 启动入口
  - `webui/app.js` 已适配 `/api/chat` + `/api/chat/think/:run_id` 异步协议
  - 新增 `tests/test_webui_server.py`、`tests/test_harness.py` 回归覆盖
  - 已完成验证：`mypy src` 通过（96 文件），`pytest` 通过（75/75），协议级冒烟通过
