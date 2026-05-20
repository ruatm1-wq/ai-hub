"""
Obsidian Local REST API wrapper

Usage:
    from common.obsidian_api import read_file, write_file, list_dir, delete_file

Environment:
    OBSIDIAN_API_KEY   — API Key (required)
    OBSIDIAN_API_URL   — default https://localhost:27124
"""

import os, ssl, json, urllib.request, urllib.parse

API_BASE = os.getenv("OBSIDIAN_API_URL", "https://localhost:27124")
AUTH_KEY = os.getenv("OBSIDIAN_API_KEY", "")

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE
_HEADERS = {"Authorization": f"Bearer {AUTH_KEY}"}


def list_dir(path: str = "") -> list:
    url = f"{API_BASE}/vault/{urllib.parse.quote(path)}"
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=10, context=_ctx) as resp:
        return json.loads(resp.read().decode()).get("files", [])


def read_file(path: str) -> str:
    req = urllib.request.Request(f"{API_BASE}/vault/{urllib.parse.quote(path)}", headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=10, context=_ctx) as resp:
        return resp.read().decode("utf-8")


def write_file(path: str, content: str) -> bool:
    data = json.dumps({"content": content}).encode("utf-8")
    url = f"{API_BASE}/vault/{urllib.parse.quote(path)}"
    req = urllib.request.Request(url, data=data, headers={**_HEADERS, "Content-Type": "application/json"}, method="PUT")
    with urllib.request.urlopen(req, timeout=10, context=_ctx):
        return True


def delete_file(path: str) -> bool:
    req = urllib.request.Request(f"{API_BASE}/vault/{urllib.parse.quote(path)}", headers=_HEADERS, method="DELETE")
    with urllib.request.urlopen(req, timeout=10, context=_ctx):
        return True
