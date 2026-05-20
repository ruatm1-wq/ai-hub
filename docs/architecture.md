# Architecture — AI Hub

[中文](#中文) | [English](#english)

---

## 中文

### 整体架构

```
┌─────────────────────────────────────┐
│          Obsidian Vault              │
│   inbox/ → write tasks               │
│   notes/ → get results               │
└──────────────┬──────────────────────┘
               │ API / File System
         ┌─────▼──────┐
         │   Watcher   │
         │  (daemon)   │
         └─────┬──────┘
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌──▼───┐
│Hermes │  │DeepSeek│  │Reas. │
│分析   │  │深度推理 │  │代码   │
└───────┘  └───────┘  └──────┘
```

### 核心组件
- **Watcher**: 监听 inbox 目录，DeepSeek 解析任务，分配到对应 Agent
- **Obsidian API**: 通过 Local REST API 插件直接读写知识库
- **Agent CLI**: 各工具的非交互模式（`exec`/`run`/`-z`）

### 环境变量
| 变量 | 说明 |
|:-----|:-----|
| OBSIDIAN_API_KEY | Obsidian 插件 API Key |
| OBSIDIAN_VAULT | Vault 路径 |
| DS_API_KEY | DeepSeek API Key |

---

## English

### Architecture

```
┌─────────────────────────────────────┐
│          Obsidian Vault              │
│   inbox/ → write tasks               │
│   notes/ → get results               │
└──────────────┬──────────────────────┘
               │ API / File System
         ┌─────▼──────┐
         │   Watcher   │
         │  (daemon)   │
         └─────┬──────┘
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌──▼───┐
│Hermes │  │DeepSeek│  │Reas. │
│Analyze│  │Reason │  │Code  │
└───────┘  └───────┘  └──────┘
```

### Components
- **Watcher**: monitors inbox, parses tasks with DeepSeek LLM, dispatches to agents
- **Obsidian API**: reads/writes vault directly via Local REST API plugin
- **Agent CLI**: non-interactive modes of each tool (`exec`/`run`/`-z`)
