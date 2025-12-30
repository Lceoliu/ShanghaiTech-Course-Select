import argparse
import os
from course_auto_select import Backends, LoginEncryptModel

__all__ = ["Backends", "LoginEncryptModel"]


if __name__ == "__main__":

    args = argparse.ArgumentParser(description="保存课程信息的工具")
    args.add_argument(
        "--config",
        type=str,
        default="./user_info.secret",
        help="用户配置文件路径",
    )
    args = args.parse_args()

    if not os.path.exists(args.config):
        print(f"配置文件 {args.config} 不存在，请先创建该文件。")
        exit(1)
    backend = Backends()
    backend.load_user_info_from_file(args.config)
    backend.login()
    print("正在保存课程信息到 courses.json 文件...")
    backend.get_student_info()
    try:
        backend._get_courses_info("./courses.json")
    except Exception as e:
        print("获取课程信息失败，错误信息如下：")
        print(e)
        exit(1)

    print("课程信息已成功保存到 courses.json 文件中。")
