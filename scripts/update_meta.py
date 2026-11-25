#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""update_meta —— 用 GitHub API 刷新条目里会过期的两个字段。

条目 frontmatter 里的 `gh_stars` 与 `pushed` 是收录那一刻的快照，仓库一有新
提交就会失真。这个脚本把最新的星标数与最近提交日期取回来，写到
data/repo-meta.json，由 src/build.py 在渲染时覆盖快照值。

只读 GitHub，不改动仓库里的任何 .md；产物与 data/link-status.json 一样属于
本地状态，不进版本库。

用法：
    GITHUB_TOKEN=... python scripts/update_meta.py
没有 GITHUB_TOKEN 时只打印提示并退出，构建会退回 frontmatter 的快照值。
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "entries"
OUT = ROOT / "data" / "repo-meta.json"

TOKEN = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
STALE_DAYS = 180          # 超过这个天数没有提交，维护活跃需要重新判定
WORKERS = 8
TIMEOUT = 20


def read_repo(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^---\s*$.*?^repo:\s*(\S+)\s*$", text, re.S | re.M)
    return m.group(1) if m else ""


def fetch(repo: str) -> dict:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "bookmarks-meta",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    return {
        "stars": int(data.get("stargazers_count") or 0),
        "pushed": (data.get("pushed_at") or "")[:10],
        "archived": bool(data.get("archived")),
        "license": ((data.get("license") or {}).get("spdx_id") or ""),
    }


def load_previous() -> dict:
    try:
        return json.loads(OUT.read_text(encoding="utf-8")).get("repos", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def main() -> int:
    if not TOKEN:
        print("未设置 GITHUB_TOKEN，跳过元数据刷新，沿用 frontmatter 快照。")
        return 0

    slugs = {}
    for path in sorted(ENTRIES.glob("*.md")):
        repo = read_repo(path)
        if repo:
            slugs[path.stem] = repo
    if not slugs:
        print("entries/ 下没有带 repo 的条目。")
        return 0

    previous = load_previous()
    result = dict(previous)
    failed = []
    archived = []

    def work(item):
        slug, repo = item
        try:
            return slug, fetch(repo), None
        except urllib.error.HTTPError as exc:
            return slug, None, f"HTTP {exc.code}"
        except Exception as exc:                       # noqa: BLE001
            return slug, None, type(exc).__name__

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for slug, info, err in pool.map(work, list(slugs.items())):
            if info is None:
                failed.append(f"{slug}({err})")
                continue
            result[slug] = info
            if info["archived"]:
                archived.append(slug)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repos": result,
    }, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

    changed = 0
    for slug, info in result.items():
        old = previous.get(slug) or {}
        if old.get("pushed") != info.get("pushed") or old.get("stars") != info.get("stars"):
            if old:
                changed += 1

    limit = datetime.now(timezone.utc) - timedelta(days=STALE_DAYS)
    stale = sorted(
        f"{result[s]['pushed']} {s}"
        for s in result
        if result[s].get("pushed") and datetime.strptime(result[s]["pushed"], "%Y-%m-%d").replace(tzinfo=timezone.utc) < limit
    )

    print(f"刷新 {len(result) - len(failed)}/{len(slugs)} 个仓库"
          f"（相对上次变化 {changed} 条；比上次多出的条目为新增）")
    if failed:
        print("失败：" + " ".join(failed))
    if archived:
        print("已归档：" + " ".join(archived))
    if stale:
        print(f"超过 {STALE_DAYS} 天没有提交（维护活跃需复核）：")
        for line in stale:
            print("  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
