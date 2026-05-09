import json

from sqlalchemy import or_

from database.db import db
from models.article import Article
from services.article_service import get_all_articles


def sync_articles_to_db():
    """
    扫描 content/articles 里的 Markdown 文件，
    然后把文章索引同步到 MySQL。
    """
    articles = get_all_articles()

    for item in articles:
        article = Article.query.filter_by(slug=item["slug"]).first()

        tags_json = json.dumps(item.get("tags", []), ensure_ascii=False)

        if article is None:
            article = Article(
                slug=item["slug"],
                title=item["title"],
                summary=item["summary"],
                category=item["category"],
                tags=tags_json,
                created_at=str(item.get("created_at", "")),
                source_url=item.get("source_url", ""),
                source_type=item.get("source_type", "manual")
            )
            db.session.add(article)
        else:
            article.title = item["title"]
            article.summary = item["summary"]
            article.category = item["category"]
            article.tags = tags_json
            article.created_at = str(item.get("created_at", ""))
            article.source_url = item.get("source_url", "")
            article.source_type = item.get("source_type", "manual")

    db.session.commit()

    return len(articles)


def get_all_articles_from_db():
    """
    从 MySQL 中读取所有文章索引。
    首页会用这个函数显示文章列表。
    """
    articles = Article.query.order_by(Article.created_at.desc()).all()

    return [article.to_dict() for article in articles]


def search_articles(keyword):
    """
    根据关键词搜索文章。

    搜索范围：
    1. 标题 title
    2. 摘要 summary
    3. 分类 category
    4. 标签 tags
    """
    keyword = keyword.strip()

    if not keyword:
        return []

    search_text = f"%{keyword}%"

    articles = Article.query.filter(
        or_(
            Article.title.like(search_text),
            Article.summary.like(search_text),
            Article.category.like(search_text),
            Article.tags.like(search_text)
        )
    ).order_by(Article.created_at.desc()).all()

    return [article.to_dict() for article in articles]


def get_articles_by_category(category_name):
    """
    根据分类名称查询文章。
    例如：分类是“编程”，就查出所有 category = 编程 的文章。
    """
    articles = Article.query.filter_by(
        category=category_name
    ).order_by(
        Article.created_at.desc()
    ).all()

    return [article.to_dict() for article in articles]


def get_articles_by_tag(tag_name):
    """
    根据标签名称查询文章。

    注意：
    tags 在 MySQL 里保存成 JSON 字符串，
    例如：["Python", "Flask", "文件读取"]

    所以这里先用 like 做简单匹配。
    后面如果项目变大，可以单独设计 tags 表。
    """
    search_text = f"%{tag_name}%"

    articles = Article.query.filter(
        Article.tags.like(search_text)
    ).order_by(
        Article.created_at.desc()
    ).all()

    return [article.to_dict() for article in articles]