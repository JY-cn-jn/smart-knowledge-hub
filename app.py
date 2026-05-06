from flask import Flask, render_template

# 创建 Flask 应用
app = Flask(__name__)


@app.route("/")
def index():
    
    # 首页路由。当用户访问 http://127.0.0.1:5000/ 时，Flask 会执行这个函数。
    # 先放几篇假文章，后面我们会改成从 Markdown 文件读取
    articles = [
        {
            "title": "智能知识库系统项目启动",
            "summary": "这是系统的第一篇测试文章。"
        },
        {
            "title": "后续功能：自动收集文章",
            "summary": "未来系统会从 RSS 自动收集知识内容。"
        },
        {
            "title": "后续功能：相关文章推荐",
            "summary": "未来每篇文章底部会显示相关内容。"
        }
    ]

    # 把 articles 数据传给 index.html 页面
    return render_template("index.html", articles=articles)


if __name__ == "__main__":
    # debug=True 表示开发模式，代码改动后会自动重启
    app.run(debug=True)