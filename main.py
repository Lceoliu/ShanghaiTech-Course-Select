# -*- coding: utf-8 -*-
import argparse
from FrontUI import FrontWindow
from Backends import Backends


if __name__ == "__main__":
    arg = argparse.ArgumentParser(description="抢课")
    arg.add_argument(
        "--config",
        type=str,
        default="./user_info.secret",
        help="配置文件路径",
    )
    arg.add_argument(
        "--id",
        type=str,
        nargs="+",
        default="",
        help="要抢的课程ID",
    )
    arg.add_argument(
        "--time",
        type=str,
        nargs="+",
        metavar="YYYY-MM-DD HH:MM",
        default="",
        help="抢课时间",
    )
    args = arg.parse_args()

    backend = Backends()

    if len(args.id) == 0 or len(args.time) == 0:
        # not use cli
        front = FrontWindow(backend)
    else:
        # use cli
        backend.load_user_info_from_file(args.config)
        backend.login()
        backend.get_student_info()
        backend._get_courses_info("./courses.json")
        import signal, time

        def signal_handler(signum, frame):
            print("Signal handler called with signal:", signum)
            backend.stop_auto_select()
            backend.close()
            exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        for id in args.id:
            backend.schedule.add_schedule(id)
        for time_str in args.time:
            import datetime

            time_obj = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            backend.schedule.add_schedule_time(time_obj)
        backend.auto_select()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            backend.stop_auto_select()
            backend.close()

        print("程序已关闭")
        backend.close()
