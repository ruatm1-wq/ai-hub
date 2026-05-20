# 🤖 AI Hub — Multi-Agent Collaboration via Obsidian

[中文](#中文) | [English](#english)

---

## 中文

> **基于 Obsidian 知识库的多 Agent 协作系统**  
> 在 Obsidian 里写一句话 → AI 自动理解 → 分配到对应 Agent → 执行 → 结果写回

### 核心特性
- 🧠 **自然语言任务**：直接写中文，AI 自动理解并分配
- 🤖 **多 Agent 协作**：Hermes(分析) / DeepSeek(深度推理) / Reasonix(代码)
- 📥 **Obsidian 集成**：inbox 写任务 → notes 出结果
- 🎬 **B站 视频总结**：粘贴链接自动提取字幕并总结
- 👀 **实时监听**：watchdog 事件 + 定时扫描双保障

### 快速开始
```bash
git clone https://github.com/ruatm1-wq/ai-hub.git
cd ai-hub

# 安装依赖
pip install -r bili-summarizer/requirements.txt
pip install watchdog

# 配置环境变量
export OBSIDIAN_API_KEY="your-api-key"
export OBSIDIAN_VAULT="/path/to/vault"

# 启动监听器
python watcher/watcher.py
```

### 项目结构
```
ai-hub/
├── bili-summarizer/     # B站视频总结工具
├── watcher/             # Obsidian 监听器
├── common/              # 共享核心模块
├── docs/                # 文档
└── README.md            # 中英双语说明
```

> 更多：`docs/architecture.md` | `docs/workflow.md`

---

## English

> **Multi-Agent Collaboration System Powered by Obsidian Knowledge Base**  
> Write a sentence in Obsidian → AI parses it → dispatches to the right Agent → writes result back

### Highlights
- 🧠 **Natural Language Tasks**: Write in plain Chinese, AI understands and routes
- 🤖 **Multi-Agent**: Hermes (analysis) / DeepSeek (deep reasoning) / Reasonix (code)
- 📥 **Obsidian Integration**: inbox → process → notes output
- 🎬 **Bilibili Video Summarizer**: Paste a link, auto-extract subtitles & summarize
- 👀 **Real-time Watching**: watchdog events + periodic scanning

### Quick Start
```bash
git clone https://github.com/ruatm1-wq/ai-hub.git
cd ai-hub

pip install -r bili-summarizer/requirements.txt
pip install watchdog

export OBSIDIAN_API_KEY="your-api-key"
export OBSIDIAN_VAULT="/path/to/vault"

python watcher/watcher.py
```

### Structure
```
ai-hub/
├── bili-summarizer/     # Bilibili video summarizer
├── watcher/             # Obsidian watcher daemon
├── common/              # Shared core modules
├── docs/                # Documentation
└── README.md            # Bilingual README
```

> More: `docs/architecture.md` | `docs/workflow.md`
