"""
Obsidian API — 通过 Local REST API 直接读写 Obsidian 知识库

比文件轮询（folder-watch）快 10 倍，实时响应。

API 地址: https://localhost:27124
认证: Bearer Token
插件: Obsidian Local REST API & MCP Server v4.0.2
"""

import os, urllib.request, json, ssl, urllib.parse
from pathlib import Path

API_BASE = "https://localhost:27124"
AUTH_KEY = os.getenv("OBSIDIAN_API_KEY", "eac04a128d77cb38f611301071d3481b158b766ac901bbbb0a6cd5f07dfe83dc")

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

_HEADERS = {"Authorization": f"Bearer {AUTH_KEY}"}


def _url(path: str) -> str:
    """把 vault 内部路径转成 API URL"""
    return f"{API_BASE}/vault/{urllib.parse.quote(path)}"


def list_dir(path: str) -> list[str]:
    """列出 vault 内某个目录的文件名列表（不含子目录）"""
    url = f"{API_BASE}/vault/{urllib.parse.quote(path)}"
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=10, context=_ctx) as resp:
        data = json.loads(resp.read().decode())
        return [f for f in data.get("files", []) if "." in f]  # 只返回文件，不含目录


def read_file(path: str) -> str:
    """读取 vault 内文件内容（v4 API 返回裸文件内容）"""
    req = urllib.request.Request(_url(path), headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=10, context=_ctx) as resp:
        return resp.read().decode("utf-8")


def write_file(path: str, content: str) -> bool:
    """写入/覆盖 vault 内文件"""
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(_url(path), data=data, headers={
        **_HEADERS, "Content-Type": "application/json",
    }, method="PUT")
    with urllib.request.urlopen(req, timeout=10, context=_ctx):
        return True


def delete_file(path: str) -> bool:
    """删除 vault 内文件"""
    req = urllib.request.Request(_url(path), headers=_HEADERS, method="DELETE")
    with urllib.request.urlopen(req, timeout=10, context=_ctx):
        return True
