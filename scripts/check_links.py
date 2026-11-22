#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check_links —— 检查每个条目的仓库状态：还活着吗、改名了吗、归档了吗。

走 GitHub API（一次请求拿到全部信息），结果写到 data/link-status.json：

  ok        正常
  archived  已归档：库还在、还能读，但作者已停止维护
  moved     改名或转移，API 会把 full_name 换成新地址
  missing   404 / 410，打不开
  unknown   网络错误、限流，不下结论

有 GITHUB_TOKEN 用 5000/h 配额，没有就走匿名 60/h——十几个仓库都够。
任何单个仓库失败都不会让脚本非零退出：链接坏了应该被标出来，而不是让整站发不出去。
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import _auth

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "entries"
SITES = ROOT / "sites"
OUT = ROOT / "data" / "link-status.json"

HEADERS = _auth.headers()

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")


def field_of(path: Path, key: str) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return ""


def repo_of(path: Path) -> str:
    return field_of(path, "repo")


def check_site(url: str) -> dict:
    """直接访问网站首页：能打开就行，不判断内容。"""
    if not url:
        return {"status": "unknown", "code": 0, "error": "缺少 url"}
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return {"status": "ok", "code": resp.status}
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 410):
            return {"status": "missing", "code": exc.code}
        if exc.code in (401, 403, 429):
            return {"status": "unknown", "code": exc.code, "error": "需要登录或被限流"}
        return {"status": "unknown", "code": exc.code}
    except Exception as exc:
        return {"status": "unknown", "code": 0, "error": f"{type(exc).__name__}: {exc}"}


def check(repo: str) -> dict:
    url = f"https://api.github.com/repos/{repo}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 410):
            return {"status": "missing", "code": exc.code}
        if exc.code == 403:
            return {"status": "unknown", "code": exc.code, "error": "限流或鉴权失败"}
        return {"status": "unknown", "code": exc.code}
    except Exception as exc:
        return {"status": "unknown", "code": 0, "error": f"{type(exc).__name__}: {exc}"}

    full = data.get("full_name") or repo
    payload = {
        "code": 200,
        "full_name": full,
        "archived": bool(data.get("archived")),
        "disabled": bool(data.get("disabled")),
        "pushed": str(data.get("pushed_at") or "")[:10],
        "stars": data.get("stargazers_count", 0),
    }
    if full.lower() != repo.lower():
        payload.update(status="moved", new_repo=full)
    elif payload["disabled"]:
        payload.update(status="missing", note="仓库被禁用")
    elif payload["archived"]:
        payload.update(status="archived")
    else:
        payload.update(status="ok")
    return payload


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print(_auth.describe())
    repos = sorted({r for r in (repo_of(p) for p in ENTRIES.glob("*.md")) if r})
    if not repos:
        print("entries/ 里没有 repo 字段")
        return 1

    items: dict[str, dict] = {}
    for repo in repos:
        result = check(repo)
        items[repo] = result
        extra = ""
        if result.get("new_repo"):
            extra = f" → {result['new_repo']}"
        elif result.get("status") == "archived":
            extra = f"（最后提交 {result.get('pushed', '?')}）"
        print(f"  {result['status']:9s} {repo}{extra}")

    site_items: dict[str, dict] = {}
    for path in sorted(SITES.glob("*.md")):
        url = field_of(path, "url")
        if not url:
            continue
        result = check_site(url)
        site_items[url] = result
        print(f"  {result['status']:9s} {url}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checked_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
        "items": items,
        "sites": site_items,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    broken = [r for r, v in items.items() if v["status"] in ("missing", "moved")]
    archived = [r for r, v in items.items() if v["status"] == "archived"]
    dead_sites = [u for u, v in site_items.items() if v["status"] == "missing"]
    print(f"\n仓库 {len(repos)} 个 · 失效/迁移 {len(broken)} · 已归档 {len(archived)}"
          f" · 网站 {len(site_items)} 个 · 打不开 {len(dead_sites)}")
    if archived:
        print("  归档：" + ", ".join(archived))
    if dead_sites:
        print("  网站打不开：" + ", ".join(dead_sites))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
