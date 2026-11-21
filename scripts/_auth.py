# -*- coding: utf-8 -*-
"""_auth —— 统一的 GitHub API 请求头。

凭据只从环境变量读取：
  GITHUB_TOKEN 或 GH_TOKEN

未设置时退回匿名请求（60 次/小时，按 IP 计）。工作流中由 Actions 自动注入
GITHUB_TOKEN，无需额外配置；本地运行时自行设置环境变量即可。
"""
from __future__ import annotations

import os

BASE = {
    "User-Agent": "gh-collection/1.0",
    "Accept": "application/vnd.github+json",
}


def token() -> str:
    return (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()


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
