# 🎬 B站 AI 总结助手 / Bilibili Video Summarizer

自动提取 B站 视频字幕并用 DeepSeek 做结构化总结。

Auto-extract subtitles from Bilibili videos and generate structured summaries with DeepSeek.

## 用法 / Usage
```bash
# 准备 cookies（将B站登录cookies放在此目录 cookies.txt）
# Prepare cookies (place B站 login cookies as cookies.txt)

# 运行
python cli.py "https://www.bilibili.com/video/BVxxx"
```

## 依赖 / Dependencies
```bash
pip install yt-dlp
```

## 输出 / Output
```json
{"title": "...", "transcript": "...", "summary": "...", "chars": 1234}
```
