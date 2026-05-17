from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from collectors.rss_collector import collect_from_rss_sources


def run_rss_collection_job():
    """
    执行一次 RSS 收集任务。
    这个函数会被 scheduler 定时调用。
    """
    print("=" * 50)
    print(f"开始执行 RSS 自动收集任务：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = collect_from_rss_sources()

    print("RSS 收集完成：")

    for item in results:
        print(f"- {item['source']}：新增 {item['new_count']} 篇文章")

    print(f"任务结束：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)


def main():
    """
    启动定时任务程序。
    """

    # 先立即执行一次，方便测试
    run_rss_collection_job()

    # 创建定时任务调度器
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    # 每天早上 9 点自动运行一次 RSS 收集任务
    scheduler.add_job(
        run_rss_collection_job,
        trigger="cron",
        hour=9,
        minute=0,
        id="daily_rss_collection"
    )

    print("定时任务已启动：每天 09:00 自动收集 RSS 文章")
    print("按 Ctrl + C 可以停止定时任务")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("定时任务已停止")


if __name__ == "__main__":
    main()