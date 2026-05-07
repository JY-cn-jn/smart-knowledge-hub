import os

from dotenv import load_dotenv
from flask import Flask, render_template, abort
import markdown

from database.db import init_database
from models.article import Article
from services.article_service import get_article_by_slug
from services.index_service import sync_articles_to_db, get_all_articles_from_db

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


@app.route("/article/<slug>")
def article_detail(slug):
    """
    文章详情页。
    根据 slug 读取对应的 Markdown 文件正文。
    """
    article = get_article_by_slug(slug)

    if article is None:
        abort(404)

    # 把 Markdown 正文转换成 HTML
    html_content = markdown.markdown(article["content"], extensions=["extra"])

    return render_template(
        "article.html",
        article=article,
        html_content=html_content
    )


if __name__ == "__main__":
    app.run(debug=True)