# catnip-agent

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
python3 -m venv .venv

# 3. 安装依赖
.venv/bin/pip install mypy pytest openai

# 4. 配置 API Key
cp apikey.txt.example apikey.txt
# 编辑 apikey.txt，填入你的 DeepSeek API Key
```

## 当前状态

**版本 0.0**（骨架 2.0）— 文档体系 + Python 工程化就绪，等待 Phase 1 开发。

## 文档

5 分钟速览：[ONBOARD.md](ONBOARD.md)
