#!/usr/bin/env python3
"""Build simple dependency-free HTML pages from the article Markdown files."""
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
GUIDES = ROOT / "guides"
GUIDES.mkdir(exist_ok=True)


def slug_for(path: Path) -> str:
    return path.stem.replace(" ", "-")


def parse_frontmatter(text: str):
    meta = {}
    if text.startswith("---"):
        _, front, body = text.split("---", 2)
        for line in front.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip().strip('"')
        return meta, body.strip()
    return meta, text


def inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def render(body: str) -> str:
    out = []
    in_list = False
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        if line.startswith("## "):
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("### "):
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{inline(line[2:])}</li>")
        elif re.match(r"^\d+\. ", line):
            if not in_list:
                out.append("<ol>"); in_list = True
            out.append(f"<li>{inline(re.sub(r'^\d+\\. ', '', line))}</li>")
        else:
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def page(title: str, category: str, content: str, slug: str) -> str:
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(title)}｜OneKey 小手册"><title>{escape(title)}｜OneKey 小手册</title><link rel="stylesheet" href="../styles.css"></head>
<body><header class="site-header"><div class="container nav"><a class="brand" href="../">OneKey <span>小手册</span></a><a class="back" href="../">返回首页</a></div></header>
<main class="container article"><p class="eyebrow">{escape(category)}</p><h1>{escape(title)}</h1><div class="article-body">{content}</div><p class="article-source">内容基于 OneKey 官方公开资料整理，具体功能和版本以官方资料为准。</p><a class="back-link" href="../">← 返回 OneKey 小手册</a></main>
<footer class="site-footer"><div class="container"><strong>OneKey 小手册</strong><p>OneKey 产品与使用资料整理站</p></div></footer></body></html>'''

for source in sorted(ARTICLES.glob("*.md")):
    meta, body = parse_frontmatter(source.read_text())
    slug = slug_for(source)
    (GUIDES / f"{slug}.html").write_text(page(meta.get("title", source.stem), meta.get("category", "使用指南"), render(body), slug))
print(f"generated {len(list(ARTICLES.glob('*.md')))} article pages")
