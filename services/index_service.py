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
        # 先看数据库里有没有这篇文章
        article = Article.query.filter_by(slug=item["slug"]).first()

        # 把 tags 列表转成 JSON 字符串，方便存入 MySQL
        tags_json = json.dumps(item.get("tags", []), ensure_ascii=False)

        if article is None:
            # 如果数据库里没有，就新增一条
            article = Article(
                slug=item["slug"],
                title=item["title"],
                summary=item["summary"],
                category=item["category"],
                tags=tags_json,
                created_at=str(item.get("created_at", ""))
            )
            db.session.add(article)
        else:
            # 如果已经存在，就更新文章索引
            article.title = item["title"]
            article.summary = item["summary"]
            article.category = item["category"]
            article.tags = tags_json
            article.created_at = str(item.get("created_at", ""))

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

    目前搜索范围：
    1. 标题 title
    2. 摘要 summary
    3. 分类 category
    4. 标签 tags

    注意：
    tags 在数据库里是 JSON 字符串，
    所以这里也可以用 like 做简单匹配。
    """
    keyword = keyword.strip()

    # 如果用户没有输入关键词，直接返回空列表
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