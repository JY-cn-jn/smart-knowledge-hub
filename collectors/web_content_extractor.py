import trafilatura


def extract_article_text(url):
    """
    根据文章 URL 提取网页正文。

    如果提取成功，返回正文文本。
    如果提取失败，返回空字符串。
    """
    if not url:
        return ""

    try:
        # 下载网页内容
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return ""

        # 从网页中提取正文
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False
        )

        if not text:
            return ""

        return text.strip()

    except Exception as error:
        # 抓取失败时不让程序崩溃
        print(f"正文提取失败：{url}")
        print(error)
        return ""