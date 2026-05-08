import json
import re

from models.article import Article


def parse_tags(tags_text):
    """
    把数据库里的 tags 字符串转成 Python list。

    数据库里保存的是 JSON 字符串：
    ["Python", "Flask", "知识库"]

    这里转成：
    ["Python", "Flask", "知识库"]
    """
    if not tags_text:
        return []

    try:
        return json.loads(tags_text)
    except json.JSONDecodeError:
        return []


def extract_words(text):
    """
    从标题或摘要中提取简单关键词。

    这里先做简单版本：
    - 英文单词可以被提取出来
    - 数字可以被提取出来
    - 中文主要依赖标签和分类来判断相关性
    """
    if not text:
        return set()

    text = text.lower()

    # 提取英文、数字等关键词
    words = re.findall(r"[a-zA-Z0-9]+", text)

    return set(words)


def calculate_related_score(current_article, other_article):
    """
    计算两篇文章之间的相关分数。
    分数越高，说明越相关。
    """
    score = 0

    # 1. 分类相同，加分
    if current_article.category and current_article.category == other_article.category:
        score += 3

    # 2. 标签重合，加分
    current_tags = set(parse_tags(current_article.tags))
    other_tags = set(parse_tags(other_article.tags))

    common_tags = current_tags.intersection(other_tags)
    score += len(common_tags) * 2

    # 3. 标题关键词重合，加分
    current_title_words = extract_words(current_article.title)
    other_title_words = extract_words(other_article.title)

    if current_title_words.intersection(other_title_words):
        score += 1

    # 4. 摘要关键词重合，加分
    current_summary_words = extract_words(current_article.summary)
    other_summary_words = extract_words(other_article.summary)

    if current_summary_words.intersection(other_summary_words):
        score += 1

    return score


def get_related_articles(slug, limit=3):
    """
    根据当前文章 slug，找出最相关的几篇文章。

    参数：
    slug：当前文章的文件名
    limit：最多推荐几篇文章
    """
    current_article = Article.query.filter_by(slug=slug).first()

    # 如果当前文章不在数据库里，直接返回空列表
    if current_article is None:
        return []

    # 找出除了当前文章以外的所有文章
    other_articles = Article.query.filter(
        Article.slug != slug
    ).all()

    scored_articles = []

    for article in other_articles:
        score = calculate_related_score(current_article, article)

        # 分数大于 0，说明有一定相关性
        if score > 0:
            scored_articles.append((score, article))

    # 按分数从高到低排序
    scored_articles.sort(key=lambda item: item[0], reverse=True)

    # 只取前 limit 篇文章
    related_articles = [
        article.to_dict()
        for score, article in scored_articles[:limit]
    ]

    return related_articles