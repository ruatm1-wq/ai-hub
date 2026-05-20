# Multi-Agent Collaboration via Obsidian

> **Write a sentence in Obsidian → AI parses it → dispatches to the right Agent → writes result back**

A multi-agent orchestration system powered by Obsidian knowledge base. Turn your note-taking app into an AI command center.

## Architecture

```
┌─────────────────────────────────────┐
│          Obsidian Vault              │
│   inbox/ → write tasks               │
│   notes/ → get results               │
└──────────────┬──────────────────────┘
               │ Obsidian Local REST API
         ┌─────▼──────┐
         │   Watcher   │
         │  (daemon)   │
         └─────┬──────┘
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌──▼───┐
│Hermes │  │DeepSeek│  │Reas. │
│Analyze│  │Reason  │  │Code  │
└───────┘  └───────┘  └──────┘
```

## Features

- 🧠 **Natural Language Tasks** — Write in plain language, AI understands and routes
- 🤖 **Multi-Agent** — Hermes (analysis), DeepSeek (deep reasoning), Reasonix (code)
- 📥 **Obsidian Integration** — inbox → process → notes output, no YAML required
- 🎬 **Bilibili Video Summarizer** — Paste a link, auto-extract subtitles & summarize
- 👀 **Auto-dispatch** — Watcher daemon monitors inbox, triggers agents automatically
- 📊 **Web Dashboard** — Real-time status at `http://localhost:8080/hub`

## Quick Start

```bash
# 1. Install Obsidian plugin: Local REST API & MCP Server v4+

# 2. Clone and setup
git clone https://github.com/ruatm1-wq/multi-agent-collaboration.git
cd multi-agent-collaboration
pip install -r requirements.txt

# 3. Set environment variables
export OBSIDIAN_API_KEY="your-obsidian-api-key"
export DS_API_KEY="your-deepseek-api-key"
export OBSIDIAN_VAULT="/path/to/vault"

# 4. Start watcher
python watcher/watcher.py

# 5. Open Obsidian, write a task in inbox/, see results in notes/
```

## Project Structure

```
multi-agent-collaboration/
├── bili-summarizer/       # Bilibili video subtitle extractor + LLM summarizer
│   ├── cli.py             # CLI entry point
│   └── README.md
├── common/                # Shared core modules
│   ├── obsidian_api.py    # Obsidian Local REST API wrapper
│   └── obsidian_bridge.py # Note parsing, frontmatter, task routing
├── watcher/               # Obsidian inbox watcher daemon
│   └── watcher.py         # Main daemon — poll, parse, dispatch, write back
├── docs/
│   ├── architecture.md    # System architecture
│   └── workflow.md        # Workflow examples
├── hub.html               # Web dashboard HTML
└── README.md
```

## How It Works

1. **Write** a task in Obsidian `inbox/` (plain Chinese or English)
2. **Watcher** detects new file, reads content
3. **DeepSeek API** parses the intent (agent, task, URL)
4. **Agent CLI** executes the task (`deepseek exec`, `hermes -z`, `reasonix run`)
5. **Result** written back to `notes/` via Obsidian API

### Task Examples

```
In inbox/:
  用Python写一个计算器，给deepseek
  → dispatches to DeepSeek for coding

In inbox/:
  Review this code and check for bugs, give to reasonix
  → dispatches to Reasonix for code review

In inbox/:
  https://www.bilibili.com/video/BVxxx
  → auto-detects Bilibili link, extracts subtitles, summarizes
```

## Environment Variables

| Variable | Description |
|:---------|:------------|
| `OBSIDIAN_API_KEY` | Obsidian Local REST API plugin key |
| `OBSIDIAN_API_URL` | API URL (default: https://127.0.0.1:27124) |
| `OBSIDIAN_VAULT` | Vault filesystem path |
| `DS_API_KEY` | DeepSeek API key for task parsing |

## Dependencies

```bash
pip install watchdog
```

## Web Dashboard

Open `http://localhost:8080/hub` for real-time status:
- Agent availability
- Task queue (pending/processing/done)
- Recent results
- Auto-refreshes every 5 seconds

## Related Repositories

- [bili-summarizer](https://github.com/ruatm1-wq/bili-summarizer) — Standalone Bilibili video summarizer

## License

MIT
