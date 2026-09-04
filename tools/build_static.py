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
    if not text.startswith("---"):
        return meta, text.strip()
    _, front, body = text.split("---", 2)
    current_list = None
    for line in front.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and current_list:
            meta[current_list].append(stripped[2:].strip().strip('"'))
        elif ":" in line:
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if not value:
                meta[key] = []
                current_list = key
            else:
                meta[key] = value.strip('"')
                current_list = None
    return meta, body.strip()


def inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def heading_id(text: str) -> str:
    value = re.sub(r"[^\w\u4e00-\u9fff -]", "", text).strip().lower()
    return re.sub(r"\s+", "-", value) or "section"


def render(body: str):
    out, headings = [], []
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
            close_list(); close_quote(); continue
        if line.startswith("> ") or line == ">":
            close_list()
            if not in_quote:
                out.append("<blockquote>"); in_quote = True
            out.append(f"<p>{inline(line[2:] if line.startswith('> ') else '')}</p>")
            continue
        close_quote()
        if line == "---":
            close_list(); out.append("<hr>"); continue
        if line.startswith("## "):
            close_list()
            title = line[3:]
            anchor = heading_id(title)
            headings.append((anchor, title))
            out.append(f'<h2 id="{anchor}">{inline(title)}</h2>')
        elif line.startswith("### "):
            close_list()
            title = line[4:]
            anchor = heading_id(title)
            headings.append((anchor, title))
            out.append(f'<h3 id="{anchor}">{inline(title)}</h3>')
        elif line.startswith("- "):
            if list_kind != "ul":
                close_list(); out.append("<ul>"); list_kind = "ul"
            out.append(f"<li>{inline(line[2:])}</li>")
        elif re.match(r"^\d+\. ", line):
            if list_kind != "ol":
                close_list(); out.append("<ol>"); list_kind = "ol"
            out.append(f"<li>{inline(re.sub(r'^\d+\\. ', '', line))}</li>")
        elif line.startswith("!["):
            close_list()
            alt = line[2:].split("]", 1)[0]
            out.append(f'<figure>{inline(line)}<figcaption>{escape(alt)}</figcaption></figure>')
        else:
            close_list(); out.append(f"<p>{inline(line)}</p>")
    close_list(); close_quote()
    return "\n".join(out), headings


def page(title, category, summary, updated, cover, sources, content, headings):
    summary = summary or "OneKey 产品与使用资料整理"
    updated = updated or "基于 OneKey 官方公开资料整理"
    cover_html = f'<div class="guide-cover"><img src="{escape(cover)}" alt="{escape(title)}"></div>' if cover else ""
    toc = "".join(f'<a href="#{escape(anchor)}">{escape(text)}</a>' for anchor, text in headings)
    source_links = "".join(f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(url)}</a>' for url in (sources or []))
    source_html = '<strong>资料来源</strong>' + (source_links or '<span>OneKey 官方公开资料</span>')
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(summary)}"><title>{escape(title)}｜OneKey 小手册</title><link rel="stylesheet" href="../styles.css"></head>
<body class="guide-page"><header class="site-header"><div class="container nav"><a class="brand" href="../">OneKey <span>小手册</span></a><a class="back" href="../">返回首页</a></div></header>
<main><section class="guide-hero"><div class="container guide-hero-inner"><div><p class="eyebrow">{escape(category)}</p><h1>{escape(title)}</h1><p class="guide-summary">{escape(summary)}</p><div class="guide-meta"><span>{escape(updated)}</span><span>阅读指南</span></div></div>{cover_html}</div></section>
<section class="container guide-layout"><article class="article-body">{content}<div class="article-source">{source_html}</div><a class="back-link" href="../">← 返回 OneKey 小手册</a></article><aside class="guide-aside"><strong>本文内容</strong>{toc or '<p>按照页面中的标题和步骤阅读即可。</p>'}<a href="../#faq">查看常见问题　→</a></aside></section></main>
<footer class="site-footer"><div class="container"><div class="footer-links"><a href="https://onekey.so/" target="_blank" rel="noopener" aria-label="OneKey 官方网站">官网</a><a href="https://help.onekey.so/" target="_blank" rel="noopener" aria-label="OneKey 帮助中心">帮助</a></div></div></footer></body></html>'''


count = 0
for source in sorted(ARTICLES.glob("*.md")):
    meta, body = parse_frontmatter(source.read_text(encoding="utf-8"))
    content, headings = render(body)
    target = GUIDES / f"{source.stem.replace(' ', '-')}.html"
    target.write_text(page(meta.get("title", source.stem), meta.get("category", "使用指南"), meta.get("summary", ""), meta.get("updated", ""), meta.get("cover", ""), meta.get("sources", []), content, headings), encoding="utf-8")
    count += 1
print(f"generated {count} article pages")
