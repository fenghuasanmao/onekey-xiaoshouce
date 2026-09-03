#!/usr/bin/env python3
"""Build dependency-free HTML guide pages from Markdown source files."""
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
GUIDES = ROOT / "guides"
GUIDES.mkdir(exist_ok=True)


def parse_frontmatter(text: str):
    meta = {}
    if text.startswith("---"):
        _, front, body = text.split("---", 2)
        for line in front.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip().strip('"')
        return meta, body.strip()
    return meta, text.strip()


def inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def render(body: str) -> str:
    out = []
    list_kind = None
    in_quote = False

    def close_list():
        nonlocal list_kind
        if list_kind:
            out.append(f"</{list_kind}>")
            list_kind = None

    def close_quote():
        nonlocal in_quote
        if in_quote:
            out.append("</blockquote>")
            in_quote = False

    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            close_list(); close_quote()
            continue
        if line.startswith("> ") or line == ">":
            close_list()
            if not in_quote:
                out.append("<blockquote>")
                in_quote = True
            out.append(f"<p>{inline(line[2:] if line.startswith('> ') else '')}</p>")
            continue
        close_quote()
        if line == "---":
            close_list(); out.append("<hr>"); continue
        if line.startswith("## "):
            close_list(); out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("### "):
            close_list(); out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("- "):
            if list_kind != "ul":
                close_list(); out.append("<ul>"); list_kind = "ul"
            out.append(f"<li>{inline(line[2:])}</li>")
        elif re.match(r"^\d+\. ", line):
            if list_kind != "ol":
                close_list(); out.append("<ol>"); list_kind = "ol"
            out.append(f"<li>{inline(re.sub(r'^\d+\\. ', '', line))}</li>")
        elif line.startswith("!["):
            close_list(); out.append(f"<figure>{inline(line)}<figcaption>{escape(line[2:].split("]", 1)[0])}</figcaption></figure>")
        else:
            close_list(); out.append(f"<p>{inline(line)}</p>")
    close_list(); close_quote()
    return "\n".join(out)


def page(title: str, category: str, summary: str, updated: str, content: str) -> str:
    summary = summary or "OneKey 产品与使用资料整理"
    updated = updated or "基于 OneKey 官方公开资料整理"
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(summary)}"><title>{escape(title)}｜OneKey 小手册</title><link rel="stylesheet" href="../styles.css"></head>
<body class="guide-page"><header class="site-header"><div class="container nav"><a class="brand" href="../">OneKey <span>小手册</span></a><a class="back" href="../">返回首页</a></div></header>
<main><section class="guide-hero"><div class="container guide-hero-inner"><p class="eyebrow">{escape(category)}</p><h1>{escape(title)}</h1><p class="guide-summary">{escape(summary)}</p><div class="guide-meta"><span>{escape(updated)}</span><span>阅读指南</span></div></div></section>
<section class="container guide-layout"><article class="article-body">{content}<div class="article-source">本文基于 OneKey 官方公开资料整理，具体功能和界面以当前版本为准。</div><a class="back-link" href="../">← 返回 OneKey 小手册</a></article><aside class="guide-aside"><strong>本文内容</strong><p>按照页面中的标题和步骤阅读即可。</p><a href="../#faq">查看常见问题 →</a></aside></section></main>
<footer class="site-footer"><div class="container"><strong>OneKey 小手册</strong><p>独立的 OneKey 产品与使用资料整理站</p></div></footer></body></html>'''

count = 0
for source in sorted(ARTICLES.glob("*.md")):
    meta, body = parse_frontmatter(source.read_text(encoding="utf-8"))
    slug = source.stem.replace(" ", "-")
    target = GUIDES / f"{slug}.html"
    target.write_text(page(meta.get("title", source.stem), meta.get("category", "使用指南"), meta.get("summary", ""), meta.get("updated", ""), render(body)), encoding="utf-8")
    count += 1
print(f"generated {count} article pages")
