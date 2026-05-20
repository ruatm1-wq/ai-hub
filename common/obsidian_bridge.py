"""
Obsidian Bridge — 读写 Obsidian 知识库的 Markdown 笔记

功能：
  1. 解析任务笔记的 frontmatter（任务描述、目标 Agent、上下文）
  2. 把结果写回 Obsidian Markdown（带 frontmatter 标记状态）
  3. 支持 inbox → tasks → archive 三级流转

frontmatter 格式：
  ---
  title: "分析Transformer论文"
  task: "用中文总结这篇论文的核心贡献和方法"
  assigned_to: "hermes"               # 首个处理的 agent
  chain: ["hermes", "deepseek-tui"]   # agent 链
  status: "pending"                   # pending / in_progress / done / failed
  source: ""                           # 论文链接或文件路径
  tags: [论文分析, transformer]
  output_to: "notes/"                 # 结果写到哪里
  created: "2026-05-20 11:00"
  ---
"""

import os, re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional


# ─── 目录结构 ─────────────────────────────────────────────
# Obsidian Vault 根
VAULT_DIR = Path(r"D:\我的工作台\02-知识库")

# 三级目录
INBOX_DIR = VAULT_DIR / "inbox"
TASKS_DIR = VAULT_DIR / "tasks"
NOTES_DIR = VAULT_DIR / "notes"
ARCHIVE_DIR = VAULT_DIR / "archive"

# 各 Agent 专用任务目录
AGENT_DIRS = {
    "hermes": TASKS_DIR / "hermes",
    "deepseek-tui": TASKS_DIR / "deepseek",
    "reasonix": TASKS_DIR / "reasonix",
    "opencode": TASKS_DIR / "opencode",
}


class ObsidianNote:
    """单条 Obsidian 笔记"""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.frontmatter: dict = {}
        self.body: str = ""
        self._parse()

    @classmethod
    def from_content(cls, content: str, title: str = "untitled"):
        """从内容字符串创建笔记（不依赖文件路径）"""
        note = cls.__new__(cls)
        note.path = Path(title)
        note.frontmatter = {}
        note.body = ""
        # 解析 frontmatter
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", content, re.DOTALL)
        if fm_match:
            yaml_text = fm_match.group(1)
            note.frontmatter = cls._parse_yaml_lite(yaml_text)
            note.body = content[fm_match.end():].strip()
        else:
            note.body = content.strip()
        return note

    def _parse(self):
        """解析 frontmatter + body"""
        if not self.path.exists():
            self.body = ""
            return

        text = self.path.read_text(encoding="utf-8")

        # 提取 frontmatter（YAML 头）
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if fm_match:
            yaml_text = fm_match.group(1)
            self.frontmatter = self._parse_yaml_lite(yaml_text)
            self.body = text[fm_match.end():].strip()
        else:
            self.frontmatter = {}
            self.body = text.strip()

    @staticmethod
    def _parse_yaml_lite(yaml_text: str) -> dict:
        """轻量 YAML 解析（只处理 frontmatter 常见格式）"""
        fm = {}
        lines = yaml_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r'^([\w_]+):\s*(.*)', line)
            if match:
                key = match.group(1)
                val = match.group(2).strip()
                # 去掉行内注释 # 
                val = re.sub(r'\s+#.*$', '', val).strip()
                # 去掉引号
                if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                    val = val[1:-1]
                # 解析列表
                if val.startswith("[") and val.endswith("]"):
                    items = re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,\[\]\s]+)', val[1:-1])
                    val = [i[0] or i[1] or i[2] for i in items]
                fm[key] = val
        return fm

    @staticmethod
    def _dump_yaml_lite(fm: dict) -> str:
        """把 dict 转成 YAML 字符串"""
        lines = ["---"]
        for key, val in fm.items():
            if isinstance(val, list):
                items = ", ".join(f'"{v}"' for v in val)
                lines.append(f"{key}: [{items}]")
            elif isinstance(val, bool):
                lines.append(f"{key}: {str(val).lower()}")
            else:
                lines.append(f'{key}: "{val}"')
        lines.append("---")
        return "\n".join(lines)

    def update_frontmatter(self, key: str, value):
        """更新/添加一条 frontmatter 字段"""
        self.frontmatter[key] = value

    def save(self):
        """写回磁盘"""
        fm_str = self._dump_yaml_lite(self.frontmatter)
        content = f"{fm_str}\n\n{self.body}"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(content, encoding="utf-8")

    @property
    def task(self) -> str:
        """获取完整的任务描述（含 body 和 source）"""
        task_text = self.frontmatter.get("task", "")
        if self.body:
            if task_text:
                task_text += f"\n\n{self.body}"
            else:
                task_text = self.body
        source = self.frontmatter.get("source", "")
        if source and source not in task_text:
            task_text += f"\n\n来源: {source}"
        return task_text.strip()

    @property
    def assigned_to(self) -> str:
        return self.frontmatter.get("assigned_to", "")

    @property
    def chain(self) -> list:
        ch = self.frontmatter.get("chain", [])
        if isinstance(ch, str):
            return [a.strip() for a in ch.split(",")]
        return ch if isinstance(ch, list) else []

    @property
    def status(self) -> str:
        return self.frontmatter.get("status", "pending")

    @property
    def output_to(self) -> str:
        return self.frontmatter.get("output_to", "notes/")

    def is_task_note(self) -> bool:
        """判断是不是一条任务笔记"""
        return bool(self.task and self.assigned_to)


def write_result(
    title: str,
    agent_name: str,
    task: str,
    result_text: str,
    success: bool,
    duration: float,
    output_subdir: str = "notes/",
) -> Path:
    """
    把执行结果写回 Obsidian 笔记。

    参数：
        title: 笔记标题
        agent_name: 执行的 Agent 名
        task: 原始任务描述
        result_text: 结果内容
        success: 是否成功
        duration: 执行耗时
        output_subdir: 输出子目录（相对知识库根目录）

    返回：
        写入的文件路径
    """
    output_dir = VAULT_DIR / output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r'[\\/:*?"<>|]', '_', title)[:60]
    filename = f"[{agent_name}]_{safe_name}.md"
    filepath = output_dir / filename

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    frontmatter = {
        "title": title,
        "agent": agent_name,
        "task": task[:200],
        "status": "done" if success else "failed",
        "duration": f"{duration}s",
        "created": now,
    }

    fm_str = ObsidianNote._dump_yaml_lite(frontmatter)
    content = f"{fm_str}\n\n## 执行结果\n\n{result_text}\n\n---\n*由编排工坊生成 | {now}*"

    filepath.write_text(content, encoding="utf-8")
    return filepath


def move_note(note: ObsidianNote, target_dir: Path) -> Path:
    """把笔记移动到目标目录（通过 API 实现跨盘移动）"""
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / note.path.name
    # 通过 API 写入新位置，删除原位置
    from obsidian_api import write_file, delete_file, list_dir
    vault_target = str(target_path).replace(str(VAULT_DIR) + "\\", "").replace("\\", "/")
    vault_src = str(note.path).replace(str(VAULT_DIR) + "\\", "").replace("\\", "/")

    # 读原内容
    try:
        content = read_file(vault_src)
    except:
        content = note.path.read_text(encoding="utf-8")

    # 写到目标
    import urllib.parse
    write_file(vault_target, content)

    # 删原文件
    try:
        delete_file(vault_src)
    except:
        pass

    note.path = target_path
    return target_path


def collect_pending_tasks() -> list[ObsidianNote]:
    """扫描 inbox/ 和各 Agent 目录，收集所有 pending 任务"""
    notes = []
    for scan_dir in [INBOX_DIR, TASKS_DIR / "hermes", TASKS_DIR / "deepseek",
                     TASKS_DIR / "reasonix", TASKS_DIR / "opencode"]:
        if not scan_dir.exists():
            continue
        for f in scan_dir.glob("*.md"):
            note = ObsidianNote(f)
            if note.is_task_note() and note.status == "pending":
                notes.append(note)
    return notes
