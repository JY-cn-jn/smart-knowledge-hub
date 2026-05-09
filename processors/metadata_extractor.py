def contains_any(text, keywords):
    """
    判断文本中是否包含任意一个关键词。
    """
    return any(keyword in text for keyword in keywords)


def add_tag(tags, tag):
    """
    添加标签，避免重复。
    """
    if tag not in tags:
        tags.append(tag)


def generate_metadata(title, summary, body="", default_category="未分类", default_tags=None):
    """
    根据文章标题、摘要、正文，自动生成分类和标签。

    第一版使用关键词规则。
    后期可以升级成 AI 自动分类。
    """
    if default_tags is None:
        default_tags = []

    # 合并文本，方便统一判断
    text = f"{title} {summary} {body}"

    category = default_category
    tags = []

    # ========== 电影 / 影视 ==========
    movie_keywords = [
        "电影", "影片", "预告", "上映", "导演", "演员", "票房",
        "奥德赛", "北美上映", "院线", "好莱坞", "剧集", "电视剧"
    ]

    if contains_any(text, movie_keywords):
        category = "电影"
        add_tag(tags, "电影")
        add_tag(tags, "影视")

        if contains_any(text, ["预告", "正式预告"]):
            add_tag(tags, "预告")

        if contains_any(text, ["上映", "北美上映"]):
            add_tag(tags, "上映")

        if contains_any(text, ["导演"]):
            add_tag(tags, "导演")

    # ========== 编程 / 开发 ==========
    programming_keywords = [
        "Python", "Flask", "JavaScript", "MySQL", "SQLAlchemy",
        "API", "后端", "前端", "数据库", "代码", "编程", "开发"
    ]

    if contains_any(text, programming_keywords):
        category = "编程"
        add_tag(tags, "编程")

        if "Python" in text:
            add_tag(tags, "Python")

        if "Flask" in text:
            add_tag(tags, "Flask")

        if "MySQL" in text:
            add_tag(tags, "MySQL")

        if "数据库" in text or "SQLAlchemy" in text:
            add_tag(tags, "数据库")

    # ========== AI / 人工智能 ==========
    ai_keywords = [
        "AI", "人工智能", "大模型", "LLM", "ChatGPT",
        "机器学习", "深度学习", "生成式 AI", "智能体"
    ]

    if contains_any(text, ai_keywords):
        category = "人工智能"
        add_tag(tags, "AI")
        add_tag(tags, "人工智能")

        if contains_any(text, ["大模型", "LLM"]):
            add_tag(tags, "大模型")

        if contains_any(text, ["智能体", "Agent"]):
            add_tag(tags, "智能体")

    # ========== 数码 / 科技产品 ==========
    digital_keywords = [
        "手机", "iPhone", "苹果", "安卓", "Mac", "电脑",
        "耳机", "相机", "数码", "硬件", "平板"
    ]

    if contains_any(text, digital_keywords):
        category = "数码"
        add_tag(tags, "数码")

        if "iPhone" in text or "苹果" in text:
            add_tag(tags, "Apple")

        if "手机" in text:
            add_tag(tags, "手机")

        if "耳机" in text:
            add_tag(tags, "耳机")

    # ========== 留学 / 教育 ==========
    study_keywords = [
        "留学", "大学", "申请", "签证", "学费", "课程",
        "研究生", "本科", "录取", "学校"
    ]

    if contains_any(text, study_keywords):
        category = "留学"
        add_tag(tags, "留学")

        if "签证" in text:
            add_tag(tags, "签证")

        if "学费" in text:
            add_tag(tags, "学费")

        if "申请" in text:
            add_tag(tags, "申请")

    # ========== 就业 / 求职 ==========
    job_keywords = [
        "求职", "简历", "面试", "岗位", "招聘", "实习",
        "就业", "薪资", "职业", "工作"
    ]

    if contains_any(text, job_keywords):
        category = "就业"
        add_tag(tags, "就业")

        if "简历" in text:
            add_tag(tags, "简历")

        if "面试" in text:
            add_tag(tags, "面试")

        if "实习" in text:
            add_tag(tags, "实习")

    # 如果没有识别出任何标签，就使用默认标签
    if not tags:
        tags = default_tags.copy()

    # 自动收集的文章保留一个来源标签
    add_tag(tags, "自动收集")

    return {
        "category": category,
        "tags": tags
    }