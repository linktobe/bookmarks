#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""repo_info —— 拉 GitHub 仓库信息 + 发版情况，输出可直接粘进收藏条目的字段。

用法：
    python repo_info.py astral-sh/uv open-webui/open-webui

「发版正规」的判定：有正式 release，且最新 tag 形如 v1.2.3 / 1.2.3（语义化版本）。
只有 commit 或日期型 tag 的不算。
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request

import _auth

API = "https://api.github.com"
HEADERS = _auth.headers()

SEMVER = re.compile(r"^(?:[A-Za-z0-9._-]*[@-])?v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def get(path: str) -> dict | list | None:
    try:
        req = urllib.request.Request(API + path, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        print(f"  ! {path} → HTTP {exc.code}", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"  ! {path} → {type(exc).__name__}: {exc}", file=sys.stderr)
        return None


def latest_tag(full_name: str) -> tuple[str, str]:
    """返回 (tag, 来源)。来源是 release / tag / 空。"""
    rel = get(f"/repos/{full_name}/releases/latest")
    if isinstance(rel, dict) and rel.get("tag_name"):
        return rel["tag_name"], "release"
    tags = get(f"/repos/{full_name}/tags?per_page=20")
    if isinstance(tags, list):
        for item in tags:
            name = item.get("name", "")
            if SEMVER.match(name):
                return name, "tag"
        if tags:
            return tags[0].get("name", ""), "tag"
    return "", ""


def summarize(full_name: str) -> None:
    repo = get(f"/repos/{full_name}")
    if not isinstance(repo, dict):
        print(f"! 拉不到 {full_name}", file=sys.stderr)
        return
    lic = (repo.get("license") or {}).get("spdx_id") or "无"
    tag, source = latest_tag(repo["full_name"])
    semver_ok = bool(tag) and bool(SEMVER.match(tag))

    print(f"repo: {repo['full_name']}")
    print(f"license: {lic}")
    print(f"language: {repo.get('language') or '—'}")
    print(f"gh_stars: {repo.get('stargazers_count', 0)}")
    print(f"pushed: {str(repo.get('pushed_at'))[:10]}")
    print(f"latest_tag: {tag or '—'}（{source or '无'}）")
    print(f"发版正规: {'✓' if semver_ok else '✗'}")
    print(f"desc: {(repo.get('description') or '').strip()}")
    print("-" * 62)


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    targets = [a.strip().rstrip("/").removeprefix("https://github.com/") for a in argv[1:]]
    if not targets:
        print(__doc__)
        return 1
    for name in targets:
        summarize(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
