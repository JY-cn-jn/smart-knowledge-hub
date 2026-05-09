import json
import re
import hashlib
import html
from datetime import date
from pathlib import Path

import feedparser

# 配置文件路径
CONFIG_PATH = Path("config/sources.json")

# Markdown 文章保存目录
CONTENT_DIR = Path("content/articles")


def load_sources():
    """
    读取 RSS 配置文件。
    """
    if not CONFIG_PATH.exists():
        return []

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def clean_text(text):
    """
    清理 RSS 里的 HTML 标签和多余空格。
    """
    if not text:
        return ""

    # 把 &amp; 这种 HTML 符号还原
    text = html.unescape(text)

    # 删除 HTML 标签
    text = re.sub(r"<[^>]+>", "", text)

    # 合并多余空格
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def safe_yaml_text(text):
    """
    简单处理 frontmatter 里的引号，避免 Markdown 头部格式出错。
    """
    if not text:
        return ""

    return text.replace("\\", "\\\\").replace('"', '\\"')


def make_slug(title, link):
    """
    根据标题和链接生成文件名 slug。
    加上链接 hash，可以减少重复文件名冲突。
    """
    title = title.lower()

    # 只保留英文、数字，其他变成 -
    title_slug = re.sub(r"[^a-z0-9]+", "-", title).strip("-")

    if not title_slug:
        title_slug = "rss-article"

    # 用链接生成短 hash，保证文件名尽量唯一
    short_hash = hashlib.sha1(link.encode("utf-8")).hexdigest()[:8]

    return f"{title_slug[:60]}-{short_hash}"


def build_markdown(title, summary, link, category, tags, created_at):
    """
    生成 Markdown 文件内容。
    """
    tags_text = "\n".join([f"  - {tag}" for tag in tags])

    return f"""---
title: "{safe_yaml_text(title)}"
summary: "{safe_yaml_text(summary)}"
category: "{safe_yaml_text(category)}"
tags:
{tags_text}
created_at: "{created_at}"
source_type: "rss"
source_url: "{safe_yaml_text(link)}"
---

# {title}

{summary}

---

原文链接：{link}
"""


def save_entry_as_markdown(entry, source):
    """
    把一条 RSS 文章保存成 Markdown 文件。
    如果文件已经存在，就跳过。
    """
    title = clean_text(entry.get("title", "Untitled"))
    link = entry.get("link", "")

    if not link:
        return False

    summary = clean_text(entry.get("summary", "暂无摘要"))

    # 优先使用 RSS 里的发布时间，没有就用今天
    created_at = entry.get("published", "")[:10] or date.today().isoformat()

    category = source.get("category", "未分类")
    tags = source.get("tags", [])

    slug = make_slug(title, link)
    file_path = CONTENT_DIR / f"{slug}.md"

    # 已经收集过就不重复保存
    if file_path.exists():
        return False

    markdown_content = build_markdown(
        title=title,
        summary=summary,
        link=link,
        category=category,
        tags=tags,
        created_at=created_at
    )

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(markdown_content)

    return True


def collect_from_rss_sources():
    """
    从所有 RSS 源收集文章。
    返回每个源新增了多少篇文章。
    """
    sources = load_sources()
    results = []

    for source in sources:
        feed = feedparser.parse(source["url"])
        limit = source.get("limit", 5)

        new_count = 0

        for entry in feed.entries[:limit]:
            saved = save_entry_as_markdown(entry, source)

            if saved:
                new_count += 1

        results.append({
            "source": source["name"],
            "new_count": new_count
        })

    return results