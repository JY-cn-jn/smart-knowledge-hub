import json
from database.db import db


class Article(db.Model):
    """
    Article 类对应 MySQL 里的 articles 表。
    一行数据代表一篇文章的索引信息。
    """

    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)

    # slug 是文章文件名，例如 flask-markdown-reading
    slug = db.Column(db.String(255), unique=True, nullable=False)

    title = db.Column(db.String(300), nullable=False)
    summary = db.Column(db.Text)
    category = db.Column(db.String(100))

    # tags 用 JSON 字符串保存，例如 ["Python", "Flask"]
    tags = db.Column(db.Text)

    # 先用字符串保存日期，后面有需要再改成 DateTime
    created_at = db.Column(db.String(50))

    def to_dict(self):
        """
        把数据库对象转换成字典，
        方便传给 HTML 页面使用。
        """
        return {
            "slug": self.slug,
            "title": self.title,
            "summary": self.summary,
            "category": self.category,
            "tags": json.loads(self.tags) if self.tags else [],
            "created_at": self.created_at
        }