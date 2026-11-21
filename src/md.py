# -*- coding: utf-8 -*-
"""md.py —— 极简 Markdown → HTML（只为 SKILL.md 这种文档服务）。

支持：YAML frontmatter、ATX 标题、围栏代码块、无序/有序列表（含一层嵌套）、
表格、引用块、分隔线、段落，以及行内的 code / 粗体 / 斜体 / 链接。
不支持：HTML 内联、脚注、图片（SKILL.md 基本用不到）。
只用标准库，Actions 里无需安装任何依赖。
"""
from __future__ import annotations

import html
import re

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_FENCE = re.compile(r"^```([\w+-]*)\s*$")
_HR = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})\s*$")
_LIST = re.compile(r"^(\s*)([-*+]|\d+\.)\s+(.*)$")
_TABLE_SEP = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$")
_CODE_SPAN = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_AUTOLINK = re.compile(r"(?<![\"'>=])(https?://[^\s<>)]+)")


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """拆出 YAML frontmatter。

    只认单行 `key: value` 和块标量（`>` / `|` / `|-` 后跟缩进内容），够 SKILL.md 用。
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    head = text[3:end]
    body = text[end + 4:].lstrip("\n")

    meta: dict[str, str] = {}
    lines = head.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line or line.lstrip().startswith("#"):
            i += 1
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value[:1] in (">", "|"):
            folded = value.startswith(">")
            block: list[str] = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in (" ", "\t")):
                block.append(lines[i].strip())
                i += 1
            meta[key] = (" " if folded else "\n").join(b for b in block if b).strip()
            continue
        meta[key] = value.strip('"').strip("'")
        i += 1
    return meta, body


def inline(text: str) -> str:
    """行内标记。先转义 HTML，再按 code → link → bold → italic 的顺序处理。"""
    out = html.escape(text, quote=False)

    slots: list[str] = []

    def keep(fragment: str) -> str:
        slots.append(fragment)
        return f"\x00{len(slots) - 1}\x00"

    out = _CODE_SPAN.sub(lambda m: keep(f"<code>{m.group(1)}</code>"), out)
    out = _LINK.sub(
        lambda m: keep(f'<a href="{html.escape(m.group(2), quote=True)}" target="_blank" '
                       f'rel="noopener noreferrer">{m.group(1)}</a>'), out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _ITALIC.sub(r"<em>\1</em>", out)
    out = _AUTOLINK.sub(
        lambda m: keep(f'<a href="{html.escape(m.group(1), quote=True)}" '
                       f'target="_blank" rel="noopener noreferrer">{m.group(1)}</a>'), out)

    for idx, fragment in enumerate(slots):          # 还原占位符（可能嵌套一轮）
        out = out.replace(f"\x00{idx}\x00", fragment)
    return out


def _render_list(lines: list[str]) -> str:
    """列表：按缩进推断层级，递归生成合法的 <ul>/<ol> 嵌套。

    之前用「栈 + 补 </li>」的写法，在 ul→ol 切换时会输出 `</ul><ol></li>` 这种
    错位标签；改成先把条目解析成 (level, tag, text)，再按层级递归渲染，
    结构天然闭合。
    """
    items: list[tuple[int, str, str]] = []
    for raw in lines:
        match = _LIST.match(raw)
        if not match:
            continue
        indent = len(match.group(1).replace("\t", "  "))
        tag = "ol" if match.group(2)[0].isdigit() else "ul"
        items.append((indent // 2, tag, match.group(3).strip()))

    def build(pos: int, level: int) -> tuple[str, int]:
        tag = items[pos][1]
        out = [f"<{tag}>"]
        while pos < len(items) and items[pos][0] == level and items[pos][1] == tag:
            text = items[pos][2]
            pos += 1
            child = ""
            if pos < len(items) and items[pos][0] > level:
                child, pos = build(pos, items[pos][0])
            out.append(f"<li>{inline(text)}{child}</li>")
        out.append(f"</{tag}>")
        return "".join(out), pos

    parts: list[str] = []
    pos = 0
    while pos < len(items):
        html, pos = build(pos, items[pos][0])
        parts.append(html)
    return "".join(parts)


def _render_table(lines: list[str]) -> str:
    def cells(row: str) -> list[str]:
        row = row.strip().strip("|")
        return [c.strip() for c in row.split("|")]

    head = cells(lines[0])
    body = [cells(line) for line in lines[2:]]
    out = ["<div class=\"table-wrap\"><table><thead><tr>"]
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def render(body: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    i = 0
    para: list[str] = []

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        fence = _FENCE.match(stripped)
        if fence:
            flush_para()
            lang = fence.group(1)
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            cls = f' class="language-{html.escape(lang, quote=True)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(code), quote=False)}</code></pre>")
            continue

        if not stripped:
            flush_para()
            i += 1
            continue

        heading = _HEADING.match(stripped)
        if heading:
            flush_para()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        if _HR.match(stripped):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            flush_para()
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").lstrip())
                i += 1
            out.append(f"<blockquote>{render(chr(10).join(quote))}</blockquote>")
            continue

        if "|" in stripped and i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1].strip()):
            flush_para()
            table: list[str] = []
            while i < len(lines) and "|" in lines[i]:
                table.append(lines[i])
                i += 1
            out.append(_render_table(table))
            continue

        if _LIST.match(line):
            flush_para()
            block: list[str] = []
            while i < len(lines) and (_LIST.match(lines[i]) or
                                      (lines[i].startswith((" ", "\t")) and lines[i].strip() and block)):
                block.append(lines[i])
                i += 1
            out.append(_render_list(block))
            continue

        para.append(stripped)
        i += 1

    flush_para()
    return "\n".join(out)
