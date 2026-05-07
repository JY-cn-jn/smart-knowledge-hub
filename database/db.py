from flask_sqlalchemy import SQLAlchemy

# 创建数据库对象
# 后面所有数据库表都会使用这个 db
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