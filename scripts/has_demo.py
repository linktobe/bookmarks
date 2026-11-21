#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""has_demo —— 判断仓库内是否有可直接查看或运行的示例。

判定依据（任一命中即算有）：
  1. 文件树中存在 examples / demo / samples / templates / fixtures 等目录
  2. 存在 *.demo.*、*.example.* 文件
  3. README 中同时出现「示例/demo/example」与可查看的产物提示（截图、在线演示、运行命令）

输出一行结论与证据，供人工复核后写入条目。
"""
from __future__ import annotations

import base64
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _auth  # noqa: E402

H = _auth.headers()
DIR_PAT = re.compile(r"(^|/)(examples?|demos?|samples?|templates?|fixtures?|playground)(/|$)", re.I)
FILE_PAT = re.compile(r"\.(demo|example|sample)\.", re.I)


def get_json(url: str):
    with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main(repos: list[str]) -> int:
    for repo in repos:
        dirs: list[str] = []
        files: list[str] = []
        try:
            info = get_json(f"https://api.github.com/repos/{repo}")
            branch = info.get("default_branch", "main")
            tree = get_json(f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1")
            for item in tree.get("tree", []):
                p = item["path"]
                if DIR_PAT.search(p):
                    top = p.split("/")[0] if "/" not in p else "/".join(p.split("/")[:2])
                    if top not in dirs:
                        dirs.append(top)
                if FILE_PAT.search(p):
                    files.append(p)
        except urllib.error.HTTPError as exc:
            print(f"{repo:42s} 拉取失败 HTTP {exc.code}")
            continue

        readme_hit = []
        try:
            data = get_json(f"https://api.github.com/repos/{repo}/readme")
            text = base64.b64decode(data["content"]).decode("utf-8", "replace")
            for m in re.finditer(r"(示例|demo|example|screenshot|截图)", text, re.I):
                readme_hit.append(m.group(0).lower())
        except Exception:
            pass

        verdict = "有示例" if (dirs or files) else ("README 提及" if readme_hit else "未见")
        print(f"{repo:42s} {verdict:10s} 目录={dirs[:3]} 文件={files[:2]} README命中={len(readme_hit)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
