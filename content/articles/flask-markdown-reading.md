---
title: "Flask 读取 Markdown 文件"
summary: "这篇文章用于测试 Flask 如何读取本地 Markdown 文件并显示到网页中。"
category: "编程"
tags:
  - Python
  - Flask
  - 文件读取
created_at: "2026-05-06"
---

# Flask 读取 Markdown 文件

Flask 不只能显示固定网页，也可以读取本地文件。

在这个项目中，我们会把文章统一保存成 Markdown 文件。

然后 Flask 会：

1. 读取 Markdown 文件
2. 提取标题、摘要、分类和标签
3. 把正文转换成 HTML
4. 显示到网页中

这样我们的知识库就有了最基础的文章系统。