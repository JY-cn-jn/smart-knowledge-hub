import json
import re
import hashlib
import html
from datetime import date
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
from collectors.web_content_extractor import extract_article_text
from processors.metadata_extractor import generate_metadata

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

def format_rss_date(entry):
    """
    把 RSS 里的发布时间转换成 YYYY-MM-DD 格式。
    如果 RSS 没有时间，就使用今天的日期。
    """
    published = entry.get("published", "")

    if not published:
        return date.today().isoformat()

    try:
        dt = parsedate_to_datetime(published)
        return dt.date().isoformat()
    except Exception:
        return date.today().isoformat()

def clean_hacker_news_summary(summary):
    """
    清理 Hacker News RSS 的摘要。

    Hacker News RSS 经常长这样：
    Article URL: ...
    Comments URL: ...
    Points: ...
    # Comments: ...

    这个函数把它整理成更适合页面显示的文字。
    """
    summary = clean_text(summary)

    if "Article URL:" not in summary:
        return summary

    article_url_match = re.search(r"Article URL:\s*(.*?)\s+Comments URL:", summary)
    points_match = re.search(r"Points:\s*(\d+)", summary)
    comments_match = re.search(r"# Comments:\s*(\d+)", summary)

    article_url = article_url_match.group(1) if article_url_match else ""
    points = points_match.group(1) if points_match else "0"
    comments = comments_match.group(1) if comments_match else "0"

    cleaned_parts = [
        "这是一篇来自 Hacker News 的文章。",
        f"热度：{points} points，{comments} comments。"
    ]

    if article_url:
        cleaned_parts.append(f"原文地址：{article_url}")

    return "\n\n".join(cleaned_parts)

def format_article_body(text, max_length=5000):
    """
    格式化网页正文。

    作用：
    1. 去掉太多空行
    2. 给段落之间加空行，方便 Markdown 显示
    3. 限制正文长度，避免页面太长
    """
    if not text:
        return ""

    # 按行拆分，去掉空行
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # 用空行连接，让 Markdown 显示成段落
    formatted_text = "\n\n".join(lines)

    # 如果正文太长，就截断
    if len(formatted_text) > max_length:
        formatted_text = formatted_text[:max_length] + "\n\n...（正文过长，已自动截断，可点击原文继续阅读）"

    return formatted_text

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


def build_markdown(title, summary, link, category, tags, created_at, body):
    """
    生成 Markdown 文件内容。

    summary：显示在文章卡片里的摘要
    body：真正的文章正文
    """
    tags_text = "\n".join([f"  - {tag}" for tag in tags])

    # 如果没有成功提取正文，就使用摘要当正文
    article_body = body.strip() if body else summary

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

{article_body}

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

    raw_summary = entry.get("summary", "暂无摘要")

    # 对 Hacker News 这种特殊摘要做简单清洗
    summary = clean_hacker_news_summary(raw_summary)

    # 把 RSS 发布时间转换成 YYYY-MM-DD
    created_at = format_rss_date(entry)

    # 尝试根据原文链接提取完整正文
    full_text = extract_article_text(link)

    # 根据文章内容自动生成分类和标签
    metadata = generate_metadata(
        title=title,
        summary=summary,
        body=full_text,
        default_category=source.get("category", "未分类"),
        default_tags=source.get("tags", [])
    )

    category = metadata["category"]
    tags = metadata["tags"]

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
        created_at=created_at,
        body=full_text
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