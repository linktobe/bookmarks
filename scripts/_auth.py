# -*- coding: utf-8 -*-
"""_auth —— 统一的 GitHub API 请求头。

凭据来源按优先级：
  1. 环境变量 GITHUB_TOKEN / GH_TOKEN
  2. 本地文件 Dev/.secrets/github_token.txt（在工作区，但不在仓库内）

令牌只需能读公开仓库，无需任何 scope。文件不存在时退回匿名请求（60 次/小时）。
"""
from __future__ import annotations

import os
from pathlib import Path

# scripts/ 的上级是项目根，再上一级是 Dev/
TOKEN_FILE = Path(__file__).resolve().parent.parent.parent.parent / ".secrets" / "github_token.txt"

BASE = {
    "User-Agent": "gh-collection/1.0",
    "Accept": "application/vnd.github+json",
}


def token() -> str:
    env = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
    if env:
        return env
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def headers() -> dict:
    head = dict(BASE)
    value = token()
    if value:
        head["Authorization"] = f"Bearer {value}"
    return head


def describe() -> str:
    """给日志用的一句话，不泄露令牌内容。"""
    value = token()
    if not value:
        return "未配置令牌（匿名，60 次/小时）"
    return f"已配置令牌（{value[:4]}…，5000 次/小时）"
