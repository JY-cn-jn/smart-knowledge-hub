---
title: "MySQL 在知识库系统中的作用"
summary: "这篇文章说明为什么知识库系统需要数据库，以及 MySQL 如何保存文章索引信息。"
category: "数据库"
tags:
  - MySQL
  - SQLAlchemy
  - 数据库
created_at: "2026-05-07"
---

# MySQL 在知识库系统中的作用

在这个项目中，Markdown 文件负责保存文章正文。

MySQL 负责保存文章的索引信息，例如：

- 标题
- 摘要
- 分类
- 标签
- 创建日期
- 文件名 slug

这样做的好处是：

1. 查询速度更快
2. 更方便做搜索
3. 更方便做分类筛选
4. 更方便做 Dashboard 统计

简单理解：

Markdown 保存内容，MySQL 负责管理和查找内容。