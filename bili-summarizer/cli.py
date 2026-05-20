"""
Bilibili Video Summarizer — CLI mode
Extract subtitles from Bilibili videos and summarize with DeepSeek API.

Usage:
    python cli.py <bilibili-video-url>

Environment:
    DS_API_KEY=your_deepseek_api_key
"""

import sys, json, subprocess, re, urllib.request, os
from pathlib import Path

BASE = Path(__file__).parent
COOKIES = BASE / "cookies.txt"
OUTPUT = BASE / "output"
DS_KEY = os.getenv("DS_API_KEY", "")


def get_subs(url):
    result = subprocess.run(
        ["yt-dlp", "--cookies", str(COOKIES), "--skip-download",
         "--write-subs", "--sub-langs", "zh+ai-zh", "--convert-subs", "srt",
         "-o", str(OUTPUT / "%(title)s"), url],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError("Failed to download subtitles")
    srt_files = list(OUTPUT.glob("*.zh.srt")) or list(OUTPUT.glob("*.ai-zh.srt"))
    if not srt_files:
        raise RuntimeError("No subtitles found")
    text = srt_files[0].read_text("utf-8")
    parts = []
    for line in text.split("\n"):
        line = line.strip()
        if re.match(r"^\d+$", line) or re.match(r"^\d+:", line):
            continue
        if line:
            parts.append(line)
    return " ".join(parts), srt_files[0].stem.replace(".zh", "").replace(".ai-zh", "")


def summarize(text, title):
    prompt = f"Summarize this video transcript in Chinese.\nFormat:\n## Summary\n## Outline\n## Key Points\n## Action Items\n\nTitle: {title}\nTranscript: {text[:8000]}"
    data = json.dumps({"model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False}).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {DS_KEY}", "Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read())["choices"][0]["message"]["content"]


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if not url:
        print(json.dumps({"error": "no url"})); sys.exit(1)
    try:
        transcript, title = get_subs(url)
        summary = summarize(transcript, title)
        print(json.dumps({"title": title, "transcript": transcript[:3000],
                          "summary": summary, "chars": len(transcript)}))
    except Exception as e:
        print(json.dumps({"error": str(e)[:300]}))
