from pathlib import Path
import frontmatter

# Markdown 文章所在的文件夹
CONTENT_DIR = Path("content/articles")


def get_all_articles():
    """
    读取所有 Markdown 文章的基本信息。
    用于首页文章列表和数据库同步。
    """
    articles = []

    for file_path in sorted(CONTENT_DIR.glob("*.md"), reverse=True):
        post = frontmatter.load(file_path)

        article = {
            "slug": file_path.stem,
            "title": post.get("title", file_path.stem),
            "summary": post.get("summary", "暂无摘要"),
            "category": post.get("category", "未分类"),
            "tags": post.get("tags", []),
            "created_at": post.get("created_at", ""),
            "source_url": post.get("source_url", ""),
            "source_type": post.get("source_type", "manual")
        }

        articles.append(article)

    return articles


def get_article_by_slug(slug):
    """
    根据文件名读取某一篇 Markdown 文章。
    用于文章详情页。
    """
    file_path = CONTENT_DIR / f"{slug}.md"

    if not file_path.exists():
        return None

    post = frontmatter.load(file_path)

    article = {
        "slug": slug,
        "title": post.get("title", slug),
        "summary": post.get("summary", "暂无摘要"),
        "category": post.get("category", "未分类"),
        "tags": post.get("tags", []),
        "created_at": post.get("created_at", ""),
        "source_url": post.get("source_url", ""),
        "source_type": post.get("source_type", "manual"),
        "content": post.content
    }

    return article