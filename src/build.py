#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build —— entries/*.md → public/（收藏夹首页 + 详情页）。

打分规则（写死在这里，改规则就改这个文件）：
五条标准每条 1 分，满足几条就是几星。

  1 开箱可用    clone/下载后在 15 分钟内能看到效果
  2 解决真问题  有明确适用场景，不是玩具
  3 维护活跃    近 6 个月有提交或发版
  4 文档够用    有可以照抄的最小示例
  5 不可替代    同类里最优或唯一

条目 frontmatter 只需要写 `met:` 里命中的标准名，星级由此推出，不手填——
这样任何一条评分都能被复核。
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))

import md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "entries"
SITES = ROOT / "sites"
PUBLIC = ROOT / "public"

SITE_TITLE = "开源收藏夹"
SITE_SUBTITLE = ("收录值得一试的开源项目。每个条目包含一句话概述、星级评定与标签。"
                 "星级由五项标准逐条判定，满足几项即为几星，评定依据均可复查。")

WEB_TITLE = "个人私藏"
WEB_SUBTITLE = ("这里收的是不在开源之列、但值得留存的网站与服务。不评星级，"
                "只记语言、费用与适用范围，正文只回答三个问题——是什么、解决什么问题、注意事项。")

# 五条标准，顺序即展示顺序
CRITERIA = [
    ("runs", "开箱即用", "下载或克隆后 15 分钟内可观察到效果"),
    ("alive", "维护活跃", "近 6 个月内有提交或发布"),
    ("docs", "文档充分", "提供可直接照用的最小示例"),
    ("release", "版本规范", "有正式发布，且版本号遵循语义化版本"),
    ("demo", "有示例", "仓库内提供可直接查看或运行的示例"),
]


LIST_JS = """<script>
(function () {
  var q = document.getElementById('q');
  var grid = document.getElementById('grid');
  var cards = [].slice.call(document.querySelectorAll('.card'));
  var empty = document.getElementById('empty');
  var active = 'all';
  function apply(animate) {
    var text = q.value.trim().toLowerCase(), shown = 0;
    if (grid) grid.classList.toggle('noanim', !animate);
    cards.forEach(function (c) {
      var ok = (!text || c.dataset.search.indexOf(text) !== -1)
        && (active === 'all' || (c.dataset.tags || '').split(' ').indexOf(active) !== -1);
      if (!ok) { c.hidden = true; return; }
      if (c.hidden) {
        c.hidden = false;
        if (animate) {
          c.style.setProperty('--i', Math.min(shown, 8));
          c.classList.remove('pop'); void c.offsetWidth; c.classList.add('pop');
        }
      }
      shown++;
    });
    empty.hidden = shown !== 0;
  }
  function setTag(value) {
    active = (value === active) ? 'all' : value;
    document.querySelectorAll('.chip').forEach(function (c) {
      c.setAttribute('aria-pressed', String(c.dataset.value === active));
    });
    apply(true);
  }
  document.querySelectorAll('.chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var on = chip.getAttribute('aria-pressed') === 'true';
      document.querySelectorAll('.chip').forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
      if (on) { active = 'all'; } else { chip.setAttribute('aria-pressed', 'true'); active = chip.dataset.value; }
      apply(true);
    });
  });
  document.querySelectorAll('.tag[data-tag]').forEach(function (tag) {
    tag.addEventListener('click', function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      setTag(tag.getAttribute('data-tag'));
    });
  });
  var wanted = new URLSearchParams(location.search).get('tag');
  if (wanted) { setTag(wanted); }
  q.addEventListener('input', function () { apply(false); });

  var chips = document.getElementById('tags');
  var toggle = document.getElementById('tagsToggle');
  if (chips && toggle) {
    var toggleTx = toggle.querySelector('.tx');
    if (wanted) chips.classList.add('open');
    var tagRowHeight = function () {
      var first = chips.firstElementChild;
      return first ? Math.round(first.getBoundingClientRect().height) : 0;
    };
    var syncTags = function () {
      var open = chips.classList.contains('open');
      var h = tagRowHeight();
      if (h) chips.style.setProperty('--row', h + 'px');
      if (open) {
        toggle.hidden = false;
      } else {
        toggle.hidden = !(chips.scrollHeight > chips.clientHeight + 1);
      }
      toggle.setAttribute('aria-expanded', String(open));
      toggleTx.textContent = open ? '收起' : '展开全部';
    };
    toggle.addEventListener('click', function () {
      chips.classList.toggle('open');
      syncTags();
    });
    syncTags();
    window.addEventListener('resize', syncTags);
    window.addEventListener('load', syncTags);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(syncTags);
  }

  function onScroll() { document.body.classList.toggle('scrolled', window.scrollY > 6); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
</script>"""


def esc(text: str) -> str:
    return html.escape(text or "", quote=True)


def stars_html(n: int) -> str:
    return "".join("★" if i < n else "☆" for i in range(len(CRITERIA)))


def fmt_count(n: int) -> str:
    if n >= 10000:
        return f"{n / 1000:.0f}k"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


SUN_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
           'stroke-linecap="round" aria-hidden="true">'
           '<circle cx="12" cy="12" r="4"/>'
           '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4'
           'M2 12h2M20 12h2M6.3 17.7l-1.4 1.4M19.1 4.9l-1.4 1.4"/></svg>')

MOON_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z"/></svg>')


def mode_switch(current: str, prefix: str = "") -> str:
    """右上角的收藏类型开关：只给图标，不写文字。"""
    oss = ' aria-current="page"' if current == "oss" else ""
    web = ' aria-current="page"' if current == "web" else ""
    return ('<nav class="mode-switch" aria-label="收藏类型">'
            f'<a class="seg" href="{prefix}index.html"{oss} '
            f'aria-label="{esc(SITE_TITLE)}" title="{esc(SITE_TITLE)}">{SUN_SVG}</a>'
            f'<a class="seg" href="{prefix}web.html"{web} '
            f'aria-label="{esc(WEB_TITLE)}" title="{esc(WEB_TITLE)}">{MOON_SVG}</a></nav>')


def favicon_link(prefix: str = "") -> str:
    return f'<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">'


def price_class(price: str) -> str:
    text = price or ""
    if "免费" in text and "付费" not in text:
        return "is-free"
    if any(word in text for word in ("付费", "订阅", "收费")):
        return "is-paid"
    return "is-unknown"


def load_link_status() -> dict:
    try:
        return json.loads((ROOT / "data" / "link-status.json").read_text(encoding="utf-8")).get("items", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_repo_meta() -> dict:
    """scripts/update_meta.py 抓回来的最新星标数与最近提交日期。"""
    try:
        return json.loads((ROOT / "data" / "repo-meta.json").read_text(encoding="utf-8")).get("repos", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_entries() -> list[dict]:
    links = load_link_status()
    fresh = load_repo_meta()
    items: list[dict] = []
    for path in sorted(ENTRIES.glob("*.md")):
        meta, body = md.split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        met_raw = [m.strip() for m in (meta.get("met") or "").split(",") if m.strip()]
        # 允许写英文 key 或中文名
        keys = []
        for name in met_raw:
            for key, label, _ in CRITERIA:
                if name in (key, label):
                    keys.append(key)
                    break
        try:
            gh_stars = int(meta.get("gh_stars") or 0)
        except ValueError:
            gh_stars = 0
        whys = {k: v for k, v in meta.items() if k.startswith("why_")}
        pushed = meta.get("pushed", "")
        live = fresh.get(path.stem) or {}
        if live.get("pushed"):
            # 评分依据里的日期跟随最新提交日期，但只改「维护活跃」成立的那类条目：
            # 判为不通过时，那句话里的日期与结论是绑在一起的，改了会自相矛盾。
            if (pushed and pushed != live["pushed"] and "alive" in keys
                    and "why_alive" in whys):
                whys["why_alive"] = whys["why_alive"].replace(pushed, live["pushed"])
            pushed = live["pushed"]
        if isinstance(live.get("stars"), int):
            gh_stars = live["stars"]
        items.append({
            "slug": path.stem,
            "title": meta.get("title") or path.stem,
            "repo": meta.get("repo", ""),
            "license": meta.get("license", ""),
            "language": meta.get("language", ""),
            "gh_stars": gh_stars,
            "pushed": pushed,
            "added": meta.get("added", ""),
            "one_liner": meta.get("one_liner", ""),
            "tags": [t.strip() for t in (meta.get("tags") or "").split(",") if t.strip()],
            "met": keys,
            "whys": whys,
            "link": links.get((meta.get("repo") or "").strip(), {}),
            "score": len(keys),
            "body": body,
        })
    items.sort(key=lambda e: (-e["score"], e["title"].lower()))
    return items


def load_sites() -> list[dict]:
    links = load_link_status().get("sites", {})
    items: list[dict] = []
    for path in sorted(SITES.glob("*.md")):
        meta, body = md.split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        url = (meta.get("url") or "").strip()
        domain = re.sub(r"^https?://(?:www\.)?", "", url).rstrip("/")
        items.append({
            "slug": path.stem,
            "title": meta.get("title") or path.stem,
            "url": url,
            "domain": domain,
            "lang": meta.get("lang", ""),
            "price": meta.get("price", ""),
            "scope": meta.get("scope", ""),
            "added": meta.get("added", ""),
            "one_liner": meta.get("one_liner", ""),
            "card": meta.get("card", ""),
            "repo": (meta.get("repo") or "").strip(),
            "tags": [t.strip() for t in (meta.get("tags") or "").split(",") if t.strip()],
            "link": links.get(url, {}),
            "body": body,
        })
    items.sort(key=lambda s: (s["added"], s["title"].lower()), reverse=True)
    return items


def gh_link_html(entry: dict) -> str:
    """卡片右上角的仓库入口：正常显示 GitHub，失效/迁移时如实标出来。"""
    repo = esc(entry["repo"])
    status = (entry.get("link") or {}).get("status", "")
    if status == "missing":
        return '<span class="gh dead mono" title="仓库已无法访问">链接失效</span>'
    if status == "moved":
        new = esc((entry.get("link") or {}).get("new_repo") or entry["repo"])
        return (f'<a class="gh moved mono" href="https://github.com/{new}" target="_blank" '
                f'rel="noopener noreferrer" title="仓库已改名或转移">已迁移 ↗</a>')
    if status == "archived":
        return (f'<a class="gh archived mono" href="https://github.com/{repo}" target="_blank" '
                f'rel="noopener noreferrer" title="作者已归档，停止维护">已归档 ↗</a>')
    return (f'<a class="gh mono" href="https://github.com/{repo}" target="_blank" '
            f'rel="noopener noreferrer">GitHub ↗</a>')


def link_warning(entry: dict) -> str:
    """详情页顶部的链接状态提示。"""
    link = entry.get("link") or {}
    status = link.get("status", "")
    if status == "missing":
        return ('<div class="banner bad"><b>仓库链接已失效。</b>'
                f'访问 github.com/{esc(entry["repo"])} 返回 {link.get("code", 404)}，'
                '该仓库可能已被删除或转为私有；本条星级仅代表收录当时的判断。</div>')
    if status == "moved":
        new = esc(link.get("new_repo") or "")
        return ('<div class="banner warn"><b>仓库已迁移。</b>'
                f'原地址现 301 重定向至 <a href="https://github.com/{new}" target="_blank" '
                f'rel="noopener noreferrer">{new}</a>；条目中的仓库名尚未更新。</div>')
    if status == "archived":
        pushed = esc(link.get("pushed") or "")
        return ('<div class="banner muted"><b>仓库已归档。</b>'
                f'代码仍可阅读，但作者已停止维护（最后提交于 {pushed or "未知"}）。'
                '星级反映收录当时的判断，不代表当前仍有维护。</div>')
    return ""


def build_index(entries: list[dict], now: str, css_ver: str) -> str:
    tags = sorted({t for e in entries for t in e["tags"]},
                  key=lambda t: (-sum(1 for e in entries if t in e["tags"]), t))
    chips = "".join(
        f'<button class="chip" type="button" data-value="{esc(t)}">'
        f'{esc(t)}<span class="n">{sum(1 for e in entries if t in e["tags"])}</span></button>'
        for t in tags)

    cards: list[str] = []
    for idx, e in enumerate(entries):
        tags_html = "".join(
            f'<button class="tag" type="button" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in e["tags"])
        searchable = " ".join([e["title"], e["one_liner"], e["repo"], " ".join(e["tags"])]).lower()
        meta_bits = [e["language"] or "—", f'{fmt_count(e["gh_stars"])} stars']
        if e["pushed"]:
            meta_bits.append(e["pushed"])
        gh = gh_link_html(e)
        cards.append(f"""      <article class="card" style="--i:{idx}"
         data-tags="{esc(' '.join(e['tags']))}" data-search="{esc(searchable)}">
        <div class="top">
          <span class="stars" title="{e['score']} / {len(CRITERIA)}">{stars_html(e['score'])}</span>
          {gh}
        </div>
        <h2><a class="stretch" href="p/{e['slug']}.html">{esc(e['title'])}</a></h2>
        <p class="repo mono">{esc(e['repo'])}</p>
        <p class="cn">{esc(e['one_liner'])}</p>
        <div class="bottom">
          <div class="tags">{tags_html}</div>
          <span class="cta mono">{esc(' · '.join(meta_bits))}</span>
        </div>
      </article>""")

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(SITE_TITLE)}</title>
<link rel="stylesheet" href="assets/style.css?v={css_ver}">
{favicon_link()}
<noscript><style>.chips{{max-height:none}}</style></noscript>
</head>
<body>
<header class="wrap">
  <div class="topline">
    <p class="eyebrow">Bookmarks · GitHub</p>
    {mode_switch('oss')}
  </div>
  <h1>{esc(SITE_TITLE)}</h1>
  <p class="lede">{esc(SITE_SUBTITLE)}</p>
  <div class="summary">
    <div><span class="k">收录</span><span class="v">{len(entries)}</span></div>
    <div><span class="k">满星</span><span class="v">{sum(1 for e in entries if e['score'] == len(CRITERIA))}</span></div>
    <div><span class="k">标签</span><span class="v">{len(tags)}</span></div>
    <div><span class="k">更新</span><span class="v">{esc(now)}</span></div>
  </div>
</header>

<div class="toolbar">
  <div class="wrap">
    <input id="q" type="search" placeholder="搜索项目、用途或标签（共 {len(entries)} 条）" autocomplete="off">
    <div class="tagbar">
      <div class="chips" id="tags">{chips}</div>
      <button class="chips-toggle" id="tagsToggle" type="button"
              aria-expanded="false" aria-controls="tags" hidden>
        <span class="tx">展开全部</span>
        <svg class="arw" width="9" height="9" viewBox="0 0 10 10" aria-hidden="true">
          <path d="M2 4l3 3 3-3" fill="none" stroke="currentColor" stroke-width="1.3"/>
        </svg>
      </button>
    </div>
  </div>
</div>

<main class="wrap">
  <div class="grid" id="grid">
{chr(10).join(cards)}
  </div>
  <p class="empty" id="empty" hidden>未找到匹配的项目。</p>
</main>

<footer class="wrap">
  <p>星级等于满足的标准项数；进入条目详情可查看逐项判定。仓库信息（语言、Star 数、最后更新时间）均为收录当日的快照。</p>
  <p class="mono">生成于 {esc(now)}</p>
</footer>

{LIST_JS}
</body>
</html>
"""


def strip_section(body: str, title: str) -> str:
    """删掉正文里的某一节（从二级标题到下一个二级标题之前）。"""
    pattern = re.compile(rf"^##[ \t]*{re.escape(title)}[ \t]*$.*?(?=^##[ \t]|\Z)",
                         re.S | re.M)
    return pattern.sub("", body).strip() + "\n"


def build_detail(entry: dict, now: str, css_ver: str) -> str:
    rows = "".join(
        f'<tr class="{"hit" if key in entry["met"] else "miss"}" style="--i:{i}">'
        f'<td class="mark">{"✓" if key in entry["met"] else "✗"}</td>'
        f'<td class="name">{esc(label)}</td>'
        f'<td class="desc">{esc(entry["whys"].get(f"why_{key}") or desc)}</td></tr>'
        for i, (key, label, desc) in enumerate(CRITERIA))
    tags_html = "".join(
        f'<a class="tag" href="../index.html?tag={quote(esc(t))}">{esc(t)}</a>'
        for t in entry["tags"])
    repo_href = f"https://github.com/{esc(entry['repo'])}"
    link = entry.get("link") or {}
    if link.get("status") == "moved" and link.get("new_repo"):
        repo_href = f"https://github.com/{esc(link['new_repo'])}"
    meta = [f'<a href="{repo_href}" target="_blank" '
            f'rel="noopener noreferrer">{esc(entry["repo"])}</a>']
    if entry["language"]:
        meta.append(f'<span>{esc(entry["language"])}</span>')
    meta.append(f'<span>{fmt_count(entry["gh_stars"])} stars</span>')
    if entry["license"]:
        meta.append(f'<span>许可：{esc(entry["license"])}</span>')
    if entry["pushed"]:
        meta.append(f'<span class="mono">更新于 {esc(entry["pushed"])}</span>')

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(entry['title'])} · {esc(SITE_TITLE)}</title>
<link rel="stylesheet" href="../assets/style.css?v={css_ver}">
{favicon_link('../')}
</head>
<body>
<header class="wrap detail-head">
  <div class="topline">
    <a class="back" href="../index.html">← 返回列表</a>
    {mode_switch('oss', '../')}
  </div>
  <h1>{esc(entry['title'])}</h1>
  <p class="score"><span class="stars big">{stars_html(entry['score'])}</span>
     <span class="score-n">{entry['score']} / {len(CRITERIA)}</span></p>
  <div class="meta">{"".join(meta)}</div>
  <div class="tags">{tags_html}</div>
</header>
<main class="wrap">
  {link_warning(entry)}
  <p class="summary-line">{esc(entry['one_liner'])}</p>
  <table class="rubric-table">
    <thead><tr><th>判定</th><th>标准</th><th>这个项目的情况</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p class="rubric-hint">表中各项均为该项目自身的判定说明。</p>
  <article class="md">{md.render(strip_section(entry['body'], '评分依据'))}</article>
</main>
<footer class="wrap">
  <p class="mono">收录于 {esc(entry['added'])} · 生成于 {esc(now)}</p>
</footer>
</body>
</html>
"""


def site_warning(site: dict) -> str:
    """网站打不开时的提示。"""
    link = site.get("link") or {}
    if link.get("status") == "missing":
        code = link.get("code", 404)
        return ('<div class="banner bad"><b>网站已无法访问。</b>'
                f'访问 {esc(site["url"])} 返回 {code}，可能已下线或限制访问；'
                '本条仅代表收录当时的判断。</div>')
    return ""


def build_web_index(sites: list[dict], now: str, css_ver: str) -> str:
    tags = sorted({t for s in sites for t in s["tags"]},
                  key=lambda t: (-sum(1 for s in sites if t in s["tags"]), t))
    chips = "".join(
        f'<button class="chip" type="button" data-value="{esc(t)}">'
        f'{esc(t)}<span class="n">{sum(1 for s in sites if t in s["tags"])}</span></button>'
        for t in tags)

    cards: list[str] = []
    for idx, s in enumerate(sites):
        tags_html = "".join(
            f'<button class="tag" type="button" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in s["tags"])
        facts = " · ".join(x for x in (s["lang"], s["price"], s["scope"]) if x)
        card_line = s.get("card") or facts
        src_link = ""
        if s.get("repo"):
            src_link = (f'<a class="gh src mono" href="https://github.com/{esc(s["repo"])}"'
                        ' target="_blank" rel="noopener noreferrer">开源 ↗</a>')
        searchable = " ".join([s["title"], s["one_liner"], s["domain"], facts,
                               " ".join(s["tags"])]).lower()
        cards.append(f"""      <article class="card" style="--i:{idx}"
         data-tags="{esc(' '.join(s['tags']))}" data-search="{esc(searchable)}">
        <div class="top">
          <span class="site-mark mono">网站</span>
          <span class="links">{src_link}<a class="gh site mono" href="{esc(s['url'])}" target="_blank"
             rel="noopener noreferrer">访问 ↗</a></span>
        </div>
        <h2><a class="stretch" href="w/{s['slug']}.html">{esc(s['title'])}</a></h2>
        <p class="repo mono">{esc(s['domain'])}</p>
        <p class="cn">{esc(s['one_liner'])}</p>
        <div class="bottom">
          <div class="tags">{tags_html}</div>
          <span class="cta mono">{esc(card_line)}</span>
        </div>
      </article>""")

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(WEB_TITLE)}</title>
<link rel="stylesheet" href="assets/style.css?v={css_ver}">
{favicon_link()}
<noscript><style>.chips{{max-height:none}}</style></noscript>
</head>
<body class="web">
<header class="wrap">
  <div class="topline">
    <p class="eyebrow">Bookmarks · Private</p>
    {mode_switch('web')}
  </div>
  <h1>{esc(WEB_TITLE)}</h1>
  <p class="lede">{esc(WEB_SUBTITLE)}</p>
  <div class="summary">
    <div><span class="k">收录</span><span class="v">{len(sites)}</span></div>
    <div><span class="k">更新</span><span class="v">{esc(now)}</span></div>
  </div>
</header>

<div class="toolbar">
  <div class="wrap">
    <input id="q" type="search" placeholder="搜索网站、用途或标签（共 {len(sites)} 个）" autocomplete="off">
    <div class="tagbar">
      <div class="chips" id="tags">{chips}</div>
      <button class="chips-toggle" id="tagsToggle" type="button"
              aria-expanded="false" aria-controls="tags" hidden>
        <span class="tx">展开全部</span>
        <svg class="arw" width="9" height="9" viewBox="0 0 10 10" aria-hidden="true">
          <path d="M2 4l3 3 3-3" fill="none" stroke="currentColor" stroke-width="1.3"/>
        </svg>
      </button>
    </div>
  </div>
</div>

<main class="wrap">
  <div class="grid" id="grid">
{chr(10).join(cards)}
  </div>
  <p class="empty" id="empty" hidden>未找到匹配的网站。</p>
</main>

<footer class="wrap">
  <p>私藏不做星级评定；语言、费用与适用范围按官网信息记录，可能随时间变动。</p>
  <p class="mono">生成于 {esc(now)}</p>
</footer>
{LIST_JS}
</body>
</html>
"""


def build_site_detail(site: dict, now: str, css_ver: str) -> str:
    rows = [("网址", f'<a href="{esc(site["url"])}" target="_blank" '
                     f'rel="noopener noreferrer">{esc(site["domain"])}</a>')]
    if site.get("repo"):
        rows.append(("开源", f'<a href="https://github.com/{esc(site["repo"])}" target="_blank" '
                            f'rel="noopener noreferrer">github.com/{esc(site["repo"])}</a>'))
    if site["lang"]:
        rows.append(("语言", esc(site["lang"])))
    if site["price"]:
        rows.append(("费用", f'<span class="{price_class(site["price"])}">'
                            f'{esc(site["price"])}</span>'))
    if site["scope"]:
        rows.append(("适用范围", esc(site["scope"])))
    if site["added"]:
        rows.append(("收录", f'<span class="mono">{esc(site["added"])}</span>'))
    meta = "".join(f'<div class="mrow"><dt>{k}</dt><dd>{v}</dd></div>' for k, v in rows)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(site['title'])} · {esc(WEB_TITLE)}</title>
<link rel="stylesheet" href="../assets/style.css?v={css_ver}">
{favicon_link('../')}
</head>
<body class="web">
<header class="wrap detail-head">
  <div class="topline">
    <a class="back" href="../web.html">← 返回列表</a>
    {mode_switch('web', '../')}
  </div>
  <h1>{esc(site['title'])}</h1>
  <dl class="meta-v">{meta}</dl>
</header>
<main class="wrap">
  {site_warning(site)}
  <p class="summary-line">{esc(site['one_liner'])}</p>
  <article class="md">{md.render(site['body'])}</article>
</main>
<footer class="wrap">
  <p class="mono">收录于 {esc(site['added'])} · 生成于 {esc(now)}</p>
</footer>
</body>
</html>
"""


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    entries = load_entries()
    if not entries:
        print("entries/ 里没有内容")
        return 1

    now = datetime.now().astimezone().strftime("%Y-%m-%d")
    (PUBLIC / "p").mkdir(parents=True, exist_ok=True)
    (PUBLIC / "w").mkdir(parents=True, exist_ok=True)
    (PUBLIC / "assets").mkdir(parents=True, exist_ok=True)
    css_bytes = (ROOT / "web" / "style.css").read_bytes()
    (PUBLIC / "assets" / "style.css").write_bytes(css_bytes)
    shutil.copyfile(ROOT / "web" / "favicon.svg", PUBLIC / "assets" / "favicon.svg")
    css_ver = hashlib.sha256(css_bytes).hexdigest()[:8]
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")

    stale = {p.name for p in (PUBLIC / "p").glob("*.html")} - {f"{e['slug']}.html" for e in entries}
    for name in stale:
        (PUBLIC / "p" / name).unlink(missing_ok=True)

    (PUBLIC / "index.html").write_text(build_index(entries, now, css_ver), encoding="utf-8")
    for entry in entries:
        (PUBLIC / "p" / f"{entry['slug']}.html").write_text(build_detail(entry, now, css_ver), encoding="utf-8")

    sites = load_sites()
    stale_w = {p.name for p in (PUBLIC / "w").glob("*.html")} - {f"{s['slug']}.html" for s in sites}
    for name in stale_w:
        (PUBLIC / "w" / name).unlink(missing_ok=True)
    (PUBLIC / "web.html").write_text(build_web_index(sites, now, css_ver), encoding="utf-8")
    for site in sites:
        (PUBLIC / "w" / f"{site['slug']}.html").write_text(build_site_detail(site, now, css_ver), encoding="utf-8")

    dist = {i: sum(1 for e in entries if e["score"] == i) for i in range(1, len(CRITERIA) + 1)}
    print("开源 %d 个 · 星级分布 %s · 非开源 %d 个" % (len(entries), dist, len(sites)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
