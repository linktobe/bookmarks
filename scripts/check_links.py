#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check_links —— 检查每个条目的仓库状态，以及 sites/ 里网站的连通性。

仓库走 GitHub API，网站直接请求首页，结果写到 data/link-status.json：

  ok        正常
  archived  已归档：库还在、还能读，但作者已停止维护
  moved     改名或转移，API 会把 full_name 换成新地址
  missing   404 / 410，打不开
  unknown   网络错误、限流、需要登录，不下结论

网站先用浏览器 UA 请求；连响应头都拿不到时，换普通客户端标识再试一次，
两次都没拿到响应头才记 unknown。

默认 24 小时内不重复检查：上次结果还在文件里且未过期时直接跳过，加 --force 可强制重查。
有 GITHUB_TOKEN 用 5000/h 配额，没有就走匿名 60/h——几十个仓库都够。
任何单个条目失败都不会让脚本非零退出：链接坏了应该被标出来，而不是让整站发不出去。
"""
from __future__ import annotations

import json
import ssl
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

MAX_AGE_HOURS = 24

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# 回落用的普通客户端标识。有些站点会掐掉「自称浏览器、指纹却不是浏览器」的请求，
# 换一个明确的非浏览器 UA 反而放行；也有站点只拦 Python-urllib 这类默认标识，
# 所以这里用自己的名字，不用库默认值。
UA_PLAIN = "gh-collection/1.0"

TIMEOUT = 25


def hours_since_last_check() -> float | None:
    """上次检查距今多少小时；没查过或读不懂返回 None。"""
    try:
        payload = json.loads(OUT.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    stamp = payload.get("checked_at_iso") or ""
    try:
        when = datetime.fromisoformat(stamp)
    except ValueError:
        return None
    if when.tzinfo is None:
        return None
    return (datetime.now(timezone.utc) - when.astimezone(timezone.utc)).total_seconds() / 3600


def field_of(path: Path, key: str) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return ""


def repo_of(path: Path) -> str:
    return field_of(path, "repo")


def probe_site(url: str, ua: str) -> tuple[dict | None, str]:
    """用指定 UA 请求一次首页。

    拿到 HTTP 响应头就返回（结论, ""）；连响应头都没拿到返回 (None, 原因)，
    由调用方决定要不要换一个 UA 重试。
    """
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return {"status": "ok", "code": resp.status}, ""
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 410):
            return {"status": "missing", "code": exc.code}, ""
        if exc.code in (401, 403, 429):
            return {"status": "unknown", "code": exc.code, "error": "需要登录或被限流"}, ""
        return {"status": "unknown", "code": exc.code}, ""
    except Exception as exc:
        reason = getattr(exc, "reason", None)
        # 有些站只发叶证书、不附中间证书。浏览器会按证书里的 AIA 地址自动补齐，
        # Python 不会，于是报「找不到本地签发者」。这不是站点故障，按可达处理并留记号。
        if isinstance(reason, ssl.SSLCertVerificationError) \
                and "local issuer certificate" in (reason.verify_message or ""):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
                    return {"status": "ok", "code": resp.status, "tls": "chain-incomplete"}, ""
            except urllib.error.HTTPError as exc2:
                if exc2.code in (404, 410):
                    return {"status": "missing", "code": exc2.code, "tls": "chain-incomplete"}, ""
                return {"status": "unknown", "code": exc2.code, "tls": "chain-incomplete"}, ""
            except Exception as exc2:
                return None, f"{type(exc2).__name__}: {exc2}"
        return None, f"{type(exc).__name__}: {exc}"


def check_site(url: str) -> dict:
    """直接访问网站首页：能打开就行，不判断内容。

    先用浏览器 UA 请求；连响应头都拿不到时（连接被重置、握手被拒、域名不通），
    换普通客户端标识再试一次——有些站点会掐掉「自称浏览器、指纹却不是浏览器」的
    请求，对普通客户端反而放行。两次都拿不到响应头才记 unknown。
    """
    if not url:
        return {"status": "unknown", "code": 0, "error": "缺少 url"}

    result, why = probe_site(url, UA)
    if result is not None:
        return result

    fallback, why2 = probe_site(url, UA_PLAIN)
    if fallback is not None:
        fallback["ua"] = "plain"
        return fallback
    return {"status": "unknown", "code": 0, "error": f"{why} · 普通标识同样失败：{why2}"}


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

    if "--force" not in sys.argv[1:]:
        age = hours_since_last_check()
        if age is not None and age < MAX_AGE_HOURS:
            print(f"上次检查距今 {age:.1f} 小时，未满 {MAX_AGE_HOURS} 小时，本次跳过"
                  f"（需要立刻重查可加 --force）。")
            return 0

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
        note = "（浏览器 UA 被拒，普通标识可达）" if result.get("ua") == "plain" else ""
        print(f"  {result['status']:9s} {url}{note}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone()
    payload = {
        "checked_at": stamp.strftime("%Y-%m-%d %H:%M"),
        "checked_at_iso": stamp.isoformat(timespec="seconds"),
        "items": items,
        "sites": site_items,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    broken = [r for r, v in items.items() if v["status"] in ("missing", "moved")]
    archived = [r for r, v in items.items() if v["status"] == "archived"]
    dead_sites = [u for u, v in site_items.items() if v["status"] == "missing"]
    rescued = [u for u, v in site_items.items() if v.get("ua") == "plain"]
    print(f"\n仓库 {len(repos)} 个 · 失效/迁移 {len(broken)} · 已归档 {len(archived)}"
          f" · 网站 {len(site_items)} 个 · 打不开 {len(dead_sites)} · 换标识可达 {len(rescued)}")
    if archived:
        print("  归档：" + ", ".join(archived))
    if dead_sites:
        print("  网站打不开：" + ", ".join(dead_sites))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
