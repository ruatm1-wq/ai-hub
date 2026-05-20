"""
AI Hub Watcher — Monitor Obsidian inbox, auto-dispatch tasks to AI agents.

Usage:
    python watcher/watcher.py

Environment:
    OBSIDIAN_API_KEY  — Obsidian Local REST API key
    DS_API_KEY        — DeepSeek API key
    OBSIDIAN_VAULT    — Vault path (default: ./)
"""

import os, sys, json, time, subprocess, re, urllib.request, ssl, urllib.parse, traceback, threading
from pathlib import Path

VAULT = Path(os.getenv("OBSIDIAN_VAULT", "."))
INBOX = VAULT / "inbox"
NOTES = VAULT / "notes"
ARCHIVE = VAULT / "archive"

API_URL = os.getenv("OBSIDIAN_API_URL", "https://127.0.0.1:27124")
API_KEY = os.getenv("OBSIDIAN_API_KEY", "")
DS_KEY = os.getenv("DS_API_KEY", "")

_seen = set()
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


def api_write(path, content):
    url = f"{API_URL}/vault/{urllib.parse.quote(path)}"
    data = json.dumps({"content": content}).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, method="PUT")
    try:
        urllib.request.urlopen(req, timeout=10, context=_ctx)
        return True
    except:
        return False


def ask_deepseek(text):
    prompt = (f"Parse task to JSON. agent: deepseek(coding) reasonix(code review) "
              f"hermes(analysis/summary). task: concise. url: extract if any.\n\n{text[:1500]}")
    data = json.dumps({"model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}], "stream": False}).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=data,
        headers={"Authorization": f"Bearer {DS_KEY}", "Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    reply = resp["choices"][0]["message"]["content"]
    try: return json.loads(reply)
    except: return {"agent": "hermes", "task": text, "url": ""}


def execute(info, filepath):
    agent = info.get("agent", "hermes")
    task = info.get("task", "")
    url = info.get("url", "")
    print(f"  Agent: {agent}  |  {task[:60]}", flush=True)

    if url and ("bilibili" in url):
        r = subprocess.run(["deepseek", "exec", "--auto", f"Summarize this Bilibili video: {url}"],
            capture_output=True, text=True, timeout=180, shell=True)
        result = r.stdout or r.stderr
    elif agent == "reasonix":
        r = subprocess.run(["reasonix", "run", task], capture_output=True, text=True, timeout=300, shell=True)
        result = r.stdout or r.stderr
    elif agent == "deepseek":
        r = subprocess.run(["deepseek", "exec", "--auto", task], capture_output=True, text=True, timeout=300, shell=True)
        result = r.stdout or r.stderr
    else:
        r = subprocess.run(["hermes", "-z", task], capture_output=True, text=True, timeout=300)
        result = r.stdout or r.stderr

    stem = Path(filepath).stem
    content = f"# Task Result\n\nAgent: {agent}\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{result[:5000]}"
    note_path = f"notes/[{agent}]_{stem}.md"
    if not api_write(note_path, content):
        (NOTES / f"[{agent}]_{stem}.md").write_text(content, encoding="utf-8")
    print(f"  Result → {note_path}", flush=True)
    ARCHIVE.mkdir(exist_ok=True)
    Path(filepath).rename(ARCHIVE / Path(filepath).name)
    print(f"  ✅ Archived\n", flush=True)


def process_file(filepath):
    key = str(filepath)
    if key in _seen: return
    _seen.add(key)
    time.sleep(1)
    try:
        text = Path(filepath).read_text("utf-8", errors="replace").strip()
        if not text: return
        if text.startswith("---"):
            parts = text.split("---", 2)
            text = parts[2] if len(parts) > 2 else text
        print(f"\n📥 {Path(filepath).name}", flush=True)
        info = ask_deepseek(text[:1000])
        execute(info, filepath)
    except Exception as ex:
        print(f"  ❌ {ex}", flush=True)


def scan_loop():
    while True:
        try:
            for f in sorted(INBOX.glob("*.md")):
                if f.name.startswith("_"): continue
                process_file(str(f))
        except: pass
        time.sleep(3)


if __name__ == "__main__":
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    for d in [INBOX, NOTES, ARCHIVE]: d.mkdir(parents=True, exist_ok=True)
    print(f"👀 Watching: {INBOX}", flush=True)

    threading.Thread(target=scan_loop, daemon=True).start()

    class Handler(FileSystemEventHandler):
        def on_created(self, e):
            if e.is_directory or not e.src_path.endswith(".md"): return
            if Path(e.src_path).name.startswith("_"): return
            time.sleep(1)
            process_file(e.src_path)

    obs = Observer()
    obs.schedule(Handler(), str(INBOX), recursive=False)
    obs.start()
    try:
        while True: time.sleep(1)
    except:
        obs.stop()
    obs.join()
