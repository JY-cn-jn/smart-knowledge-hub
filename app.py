from flask import Flask, render_template, abort
import markdown

from services.article_service import get_all_articles, get_article_by_slug

# 创建 Flask 应用
app = Flask(__name__)


@app.route("/")
def index():
    """
    首页路由。
    显示所有 Markdown 文章。
    """
    articles = get_all_articles()
    return render_template("index.html", articles=articles)


@app.route("/article/<slug>")
def article_detail(slug):
    """
    文章详情页。
    根据 slug 读取指定 Markdown 文件。
    """
    article = get_article_by_slug(slug)

    # 如果文章不存在，显示 404
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
    # debug=True 表示开发模式
    app.run(debug=True)