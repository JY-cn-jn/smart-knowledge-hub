import os

from dotenv import load_dotenv
from flask import Flask, render_template, abort, request
import markdown

from database.db import init_database
from models.article import Article
from services.article_service import get_article_by_slug
from services.index_service import (
    sync_articles_to_db,
    get_all_articles_from_db,
    search_articles,
    get_articles_by_category,
    get_articles_by_tag
)
from services.dashboard_service import get_dashboard_stats
from services.related_service import get_related_articles

# 读取 .env 文件
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)

# 从 .env 中读取数据库连接地址
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

# 关闭一个不必要的追踪功能，避免警告
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 初始化数据库
init_database(app)


@app.route("/")
def index():
    """
    首页路由。
    先把 Markdown 文章同步到 MySQL，
    再从 MySQL 读取文章列表。
    """
    sync_articles_to_db()
    articles = get_all_articles_from_db()

    return render_template("index.html", articles=articles)


@app.route("/search")
def search():
    """
    搜索页面。
    从 URL 里读取 q 参数，然后搜索文章。
    例如：/search?q=Flask
    """
    keyword = request.args.get("q", "").strip()

    sync_articles_to_db()
    results = search_articles(keyword)

    return render_template(
        "search.html",
        keyword=keyword,
        articles=results
    )


@app.route("/category/<category_name>")
def category_page(category_name):
    """
    分类筛选页面。
    例如：/category/编程
    """
    sync_articles_to_db()
    articles = get_articles_by_category(category_name)

    return render_template(
        "filter.html",
        page_title=f"分类：{category_name}",
        description=f"这里显示所有属于「{category_name}」分类的文章。",
        articles=articles
    )


@app.route("/tag/<tag_name>")
def tag_page(tag_name):
    """
    标签筛选页面。
    例如：/tag/Flask
    """
    sync_articles_to_db()
    articles = get_articles_by_tag(tag_name)

    return render_template(
        "filter.html",
        page_title=f"标签：{tag_name}",
        description=f"这里显示所有带有「{tag_name}」标签的文章。",
        articles=articles
    )


@app.route("/dashboard")
def dashboard():
    """
    Dashboard 统计页。
    显示文章数量、分类数量、标签数量和最近文章。
    """
    sync_articles_to_db()
    stats = get_dashboard_stats()

    return render_template("dashboard.html", stats=stats)


@app.route("/article/<slug>")
def article_detail(slug):
    """
    文章详情页。
    根据 slug 读取对应的 Markdown 文件正文。
    同时计算相关文章。
    """
    # 先同步一次，保证数据库里有最新文章索引
    sync_articles_to_db()

    article = get_article_by_slug(slug)

    if article is None:
        abort(404)

    # 把 Markdown 正文转换成 HTML
    html_content = markdown.markdown(article["content"], extensions=["extra"])

    # 获取相关文章
    related_articles = get_related_articles(slug, limit=3)

    return render_template(
        "article.html",
        article=article,
        html_content=html_content,
        related_articles=related_articles
    )


if __name__ == "__main__":
    app.run(debug=True)