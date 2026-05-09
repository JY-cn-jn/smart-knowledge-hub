from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

# 创建数据库对象
db = SQLAlchemy()


def init_database(app):
    """
    初始化数据库。
    把 Flask app 和 SQLAlchemy 连接起来，
    并根据模型自动创建表。
    """
    db.init_app(app)

    with app.app_context():
        # 如果表不存在，就自动创建
        db.create_all()

        # 如果旧表缺少新字段，就自动补上
        ensure_article_columns()


def ensure_article_columns():
    """
    给旧的 articles 表补充新字段。
    因为 db.create_all() 不会修改已经存在的表结构。
    """
    inspector = inspect(db.engine)

    if not inspector.has_table("articles"):
        return

    columns = [column["name"] for column in inspector.get_columns("articles")]

    if "source_url" not in columns:
        db.session.execute(text("ALTER TABLE articles ADD COLUMN source_url TEXT"))

    if "source_type" not in columns:
        db.session.execute(text("ALTER TABLE articles ADD COLUMN source_type VARCHAR(50) DEFAULT 'manual'"))

    db.session.commit()