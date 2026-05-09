from collectors.rss_collector import collect_from_rss_sources


def main():
    """
    手动运行 RSS 收集任务。
    """
    results = collect_from_rss_sources()

    print("RSS 收集完成：")

    for item in results:
        print(f"- {item['source']}：新增 {item['new_count']} 篇文章")


if __name__ == "__main__":
    main()