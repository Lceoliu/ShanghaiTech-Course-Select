"""Command line entry point for course auto selection."""

from __future__ import annotations

import argparse
import signal
import time
from typing import Iterable, Optional

from .backends import Backends
from .ui import FrontWindow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="课堂抢课工具")
    parser.add_argument(
        "--config",
        type=str,
        default="./user_info.secret",
        help="用户配置文件路径",
    )
    # 此功能已被独立为 get_courses.py 脚本
    # parser.add_argument(
    #     "--save-courses",
    #     type=str,
    #     default="./courses.json",
    #     help="保存课程信息的文件路径, 用于获取本学期所有课程对应的 ID， 请在每次学期开始后更新该文件",
    # )
    parser.add_argument(
        "--id",
        type=str,
        nargs="+",
        default="",
        help="要抢的课程 ID 列表",
    )
    parser.add_argument(
        "--time",
        type=str,
        nargs="+",
        metavar="YYYY-MM-DD HH:MM",
        default="",
        help="抢课触发时间",
    )
    return parser


def run_cli(ids: Iterable[str], times: Iterable[str], config_path: str) -> None:
    backend = Backends()
    backend.load_user_info_from_file(config_path)
    backend.login()
    backend.get_student_info()
    backend._get_courses_info("./courses.json")

    def signal_handler(signum, _frame):
        print("Signal handler called with signal:", signum)
        backend.stop_auto_select()
        backend.close()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, signal_handler)

    for course_id in ids:
        backend.schedule.add_schedule(course_id)
    for time_str in times:
        import datetime

        time_obj = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        backend.schedule.add_schedule_time(time_obj)

    backend.auto_select()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        backend.stop_auto_select()
    finally:
        backend.close()
        print("程序已关闭")


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    backend = Backends()

    if len(args.id) == 0 or len(args.time) == 0:
        FrontWindow(backend)
        return

    run_cli(args.id, args.time, args.config)


if __name__ == "__main__":
    main()
