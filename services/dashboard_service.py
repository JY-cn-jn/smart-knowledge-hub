import json
from collections import Counter

from models.article import Article


def get_dashboard_stats():
    """
    统计知识库的整体数据。
    用于 Dashboard 页面。
    """

    # 读取所有文章
    articles = Article.query.order_by(Article.created_at.desc()).all()

    total_articles = len(articles)

    category_counter = Counter()
    tag_counter = Counter()

    # 遍历所有文章，统计分类和标签
    for article in articles:
        if article.category:
            category_counter[article.category] += 1

        if article.tags:
            try:
                tags = json.loads(article.tags)
            except json.JSONDecodeError:
                tags = []

            for tag in tags:
                tag_counter[tag] += 1

    # 最近新增文章，先取前 5 篇
    recent_articles = [
        article.to_dict()
        for article in articles[:5]
    ]

    return {
        "total_articles": total_articles,
        "total_categories": len(category_counter),
        "total_tags": len(tag_counter),
        "category_stats": category_counter.most_common(),
        "tag_stats": tag_counter.most_common(10),
        "recent_articles": recent_articles
    }