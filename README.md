# catnip-agent

> 🪟 **Windows 特化版本** — 本仓库为 Windows 平台优化的 catnip-agent 脚手架。
> 所有路径、命令、默认配置均以 **Windows 优先**，同时兼容 Linux/macOS。

Python 实现的 11 层 Coding Agent Runtime。

```
gateway_01 → queue_02 → worker_03 → harness_04 → context_05 → skills_06
→ memory_07 → runner_08 → eventbus_09 → tool_registry_10 → executor_11
```

## 快速开始

```bash
# 1. 克隆
git clone git@github.com:howtio/catnipthon.git
cd catnipthon

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境（Windows）
.venv\Scripts\activate
# 或（Linux/macOS）
# source .venv/bin/activate

# 4. 安装依赖
.venv\Scripts\pip install mypy pytest openai

# 5. 配置 API Key
cp apikey.txt.example apikey.txt        # Git Bash / Linux/macOS
# copy apikey.txt.example apikey.txt    # Windows cmd.exe
# 编辑 apikey.txt，填入你的 DeepSeek API Key
```

## 当前状态

**版本 7.0**（Windows 特化脚手架 3.0）

主线仓库：[https://github.com/howtio/catnipthon](https://github.com/howtio/catnipthon)

## Web UI

仓库内置一个情书风格前端，目录在 [webui](C:/Users/HP/OneDrive/Desktop/agentui/catnipthon-main/webui)。

建议通过 catnip 运行时启动，而不是直接双击 `index.html`：

```powershell
python -m src.main --webui
```

默认地址：

```text
http://127.0.0.1:8765
```

这样前端会通过 `/api/chat` 调用现有 harness，而不是走本地 mock 回复。

## 文档

5 分钟速览：[ONBOARD.md](ONBOARD.md)
