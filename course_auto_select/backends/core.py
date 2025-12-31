# -*- coding: utf-8 -*-
# @Time    : 2025/05/22
# @Author  : Chang


from .encryption import LoginEncryptModel
from .schedule import ScheduleAutoSelector
from .my_utils import *
import requests
import random
import time
import threading
import logging
import json
import os
import bs4

from typing import Optional, Union, List, Dict
from datetime import datetime, timedelta
from pathlib import Path


class Backends:
    def __init__(self):
        self.cookies = {
            'Max-Age': '0',
            'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE': 'zh_CN',
            'JSESSIONID': '',
            'route': '',
        }
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'null',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        self.auth_url = "https://ids.shanghaitech.edu.cn/authserver/login?service=https%3A%2F%2Fegate-new.shanghaitech.edu.cn%2Flogin"

        self.encrypt_model = LoginEncryptModel()

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        self.username = None
        self.password = None
        self.semester_id = None

        self.is_logged_in = False
        self.login_attempts = 0
        self.login_max_retries = 3
        self.need_captcha = False

        self.courses_info: List[Dict] = None
        self.student_info = None

        self.give_up_seconds: int = 30
        self.schedule = ScheduleAutoSelector(delay_seconds=self.give_up_seconds)
        self.auto_select_cd: float = 0.25

        # status & logger module
        self.status = []
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        )
        self.logger = logging.getLogger("BackendLogger")
        self.logger.setLevel(logging.INFO)
        self.logging_file_path = Path("logs")
        if not self.logging_file_path.exists():
            self.logging_file_path.mkdir(parents=True)
        self.logging_file_handler = logging.FileHandler(
            f"logs/backend_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        )
        self.logging_file_handler.setLevel(logging.INFO)
        self.logging_file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(self.logging_file_handler)

        self.thread_lock = threading.Lock()
        self.stop_event = threading.Event()

        self.logger.info("Backend initialized.")

    def load_user_info_from_file(self, path: str = "./user_info.secret"):
        if not Path(path).exists():
            self.logger.error(f"User info file not found: {path}")
            raise FileNotFoundError(f"User info file not found: {path}")
        try:
            import configparser

            config = configparser.ConfigParser()
            config.read(path)
            user_info = {
                "username": config.get("user_info", "username"),
                "password": config.get("user_info", "password"),
            }
        except ImportError:
            self.logger.warning("no configparser module found, using json instead.")
            import json

            with open(path, "r") as f:
                user_info = json.load(f)
        except Exception as e:
            if "File contains no section headers" in str(e):
                self.logger.warning("User info file format error, try parsing anyway.")
                # This is the oldest version of config file, should never be used
                with open(path, "r") as f:
                    user_name = (
                        f.readline().strip().replace("Username = ", "").replace('"', "")
                    )
                    password = (
                        f.readline().strip().replace("Password = ", "").replace('"', "")
                    )
                user_info = {"username": user_name, "password": password}
            else:
                raise e
        self.username = user_info["username"]
        self.password = user_info["password"]

    def login(self, username: str = None, password: str = None):
        if username is None or password is None:
            if self.username is None or self.password is None:
                self.logger.error("Username and password must be provided.")
                raise ValueError("Username and password must be provided.")
            username = self.username
            password = self.password
        else:
            self.username = username
            self.password = password

        self.data = {
            'username': username,
            'password': '',
            'captcha': '',
            '_eventId': 'submit',
            'cllt': 'userNameLogin',
            'dllt': 'generalLogin',
            'lt': '',
            'execution': '',
        }
        first_response = self.session.get(self.auth_url, cookies=self.cookies)
        self._parse_login_page(first_response.text)

        while not self.is_logged_in and self.login_attempts < self.login_max_retries:
            captcha_response = self.session.get(
                f"https://ids.shanghaitech.edu.cn/authserver/checkNeedCaptcha.htl?username={username}&_={int(time.time()*1000)}"
            )

            try:
                self.need_captcha = captcha_response.json().get('isNeed')
            except Exception as e:
                self.logger.error(f"Error checking captcha: {e}")
                self.need_captcha = False
            self.logger.info(
                f"Login attempts: {self.login_attempts+1}/{self.login_max_retries}"
            )
            self.status.append(
                f"Login attempts: {self.login_attempts+1}/{self.login_max_retries}"
            )
            if self.need_captcha:
                self.logger.info("Captcha required.")
                self.status.append("Captcha required.")
                captcha_code = self._get_captcha_code()
                self._submit_login(captcha_code)
            else:
                self._submit_login()

            self.login_attempts += 1
        if not self.is_logged_in:
            self.logger.warning("Login attempts exceeded maximum retries.")
            self.status.append("Login attempts exceeded maximum retries.")

    def _parse_login_page(self, html: str):
        import bs4

        res = bs4.BeautifulSoup(html, 'lxml')
        salt = res.select("#pwdEncryptSalt")[0]['value']
        execution = res.select("#execution")[0]['value']

        self.encrypt_model.set_salt(salt)
        if self.data:
            self.data['execution'] = execution
        else:
            raise ValueError("Data is not set.")

    def _get_captcha_code(self):
        # This method should implement the logic to get the captcha code from the user
        # For now, we will just return a dummy value
        return "dummy_captcha"

    def _submit_login(self, captcha_code=None):
        if captcha_code:
            self.data['captcha'] = captcha_code

        encrypted_password = self.encrypt_model.encrypt_password(self.password)
        self.data['password'] = encrypted_password

        response = self.session.post(
            self.auth_url,
            data=self.data,
        )
        self.session.cookies.update(response.cookies)
        if response.status_code == 200:
            self.logger.info("Login successful!")
            self.status.append("Login successful!")
            self.is_logged_in = True
        else:
            self.logger.error("Login failed!")
            self.status.append("Login failed!")
            if "您提供的用户名或者密码有误" in response.text:
                self.logger.error("您提供的用户名或者密码有误")
                self.status.append("您提供的用户名或者密码有误")
            self.is_logged_in = False

    def get_eams_home(self):
        home_url = (
            "https://eams.shanghaitech.edu.cn/eams/home!childmenus.action?menu.id=165"
        )
        response = self.session.get(home_url, cookies=self.cookies)
        self.session.cookies.update(response.cookies)
        if response.status_code == 200:
            print("EAMS home page accessed successfully.")
            self.status.append("EAMS home page accessed successfully.")
            return response.text
        else:
            print("Failed to access EAMS home page.")
            self.status.append("Failed to access EAMS home page.")
            return None

    def _get_student_info_raw(self):
        student_info_url = "https://eams.shanghaitech.edu.cn/eams/stdDetail.action"
        response = self.session.get(student_info_url, cookies=self.cookies)
        if response.status_code == 200:
            print("Student info accessed successfully.")
            self.status.append("Student info accessed successfully.")
            # print(response.text)
            return response.text
        else:
            print("Failed to access student info.")
            self.status.append("Failed to access student info.")
            return None

    def get_student_info(self) -> Optional[Dict[str, str]]:
        student_info = self._get_student_info_raw()
        if student_info:
            import bs4

            soup = bs4.BeautifulSoup(student_info, 'lxml')
            student_info_text = soup.text
            import re

            # 使用正则表达式提取关键信息
            student_name_match = re.search(r'姓名：\s*([^\n]+)', student_info_text)
            grade_match = re.search(r'年级：\s*([^\n]+)', student_info_text)
            major_match = re.search(r'专业：\s*([^\n]+)', student_info_text)
            college_match = re.search(r'院系：\s*([^\n]+)', student_info_text)
            student_id_match = re.search(r'学号：\s*([^\n]+)', student_info_text)

            # 提取匹配结果或设置默认值
            student_name = (
                student_name_match.group(1).strip() if student_name_match else "未知"
            )
            grade = grade_match.group(1).strip() if grade_match else "未知"
            major = major_match.group(1).strip() if major_match else "未知"
            college = college_match.group(1).strip() if college_match else "未知"
            student_id = (
                student_id_match.group(1).strip() if student_id_match else "未知"
            )

            self.logger.info(f"Student Name: {student_name}")
            self.status.append(
                f"Student Name: {student_name}, Grade: {grade}, Major: {major}"
            )
            self.student_info = {
                "student_name": student_name,
                "grade": grade,
                "major": major,
            }

            return self.student_info
        else:
            self.logger.warning("No student info available.")
            self.status.append("No student info available.")
            return None

    def _get_semester_id(self):
        entering_page_url = (
            "https://eams.shanghaitech.edu.cn/eams/stdElectCourse.action"
        )

        response = self.session.get(entering_page_url, cookies=self.cookies)
        if response.status_code == 200:
            print("Entering page accessed successfully.")
            self.status.append("Entering page accessed successfully.")
        else:
            print("Failed to access entering page.")
            self.status.append("Failed to access entering page.")
            return None

        import bs4

        soup = bs4.BeautifulSoup(response.text, 'lxml')
        try:
            semester_id = soup.select("a")[0]['href'].split('id=')[1]
            self.semester_id = semester_id
            return semester_id
        except Exception as e:
            print(f"Error occurred while parsing semester ID: {e}")
            self.status.append(f"Error occurred while parsing semester ID: {e}")
            return None

    def get_course_selection_page(self):
        select_course_url = f"https://eams.shanghaitech.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id={self._get_semester_id()}"
        response = self.session.get(select_course_url, cookies=self.cookies)
        self.session.cookies.update(response.cookies)
        self.cookies.update(response.cookies)
        if response.status_code == 200:
            self.logger.info("Course selection page accessed successfully.")
            self.status.append("Course selection page accessed successfully.")
            return response.text
        else:
            self.logger.error("Failed to access course selection page.")
            self.status.append("Failed to access course selection page.")
            return None

    def load_courses_info(
        self, path: str = "courses.json"
    ) -> Union[None, Dict[str, str]]:
        """Load course information from a JSON file.

        Args:
            path (str, optional): The path to the JSON file. Defaults to "courses.json".

        Returns:
            _type_: _dict_: A dictionary containing course information.
        """
        import json, os

        path = os.path.join(os.getcwd(), path)
        if not os.path.exists(path):
            print(f"File {path} not found.")
            self.status.append(f"File {path} not found.")
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            self.status.append(f"Error decoding JSON: {e}")
            return None
        except Exception as e:
            print(f"Error loading file: {e}")
            self.status.append(f"Error loading file: {e}")
            return None

        self.courses_info = data
        print(f"Loaded courses info from {path}.")
        self.status.append(f"Loaded courses info from {path}.")
        return data

    def _get_courses_info(
        self, save_to_path: Optional[str] = None
    ) -> Optional[list[dict]]:
        def ParseCourseDatas(res_text):
            import ast, re

            # 添加引号的正则表达式替换函数
            def add_quotes(match):
                return f'"{match.group(0)}"'

            # 使用正则表达式添加引号
            adjusted_string = re.sub(r"(?<=({|,))(\w+)(?=(}|:))", add_quotes, res_text)
            adjusted_string = re.sub(
                r"(?<=(:))(\w+|\d\.\d)(?=(,|}))", add_quotes, adjusted_string
            )
            dic = ast.literal_eval(adjusted_string)
            return dic

        def ParseFaultCallback(js_code: str) -> Optional[dict]:
            import tempfile

            with tempfile.NamedTemporaryFile(
                suffix=".js", mode="w", delete=False, encoding="utf-8"
            ) as f:
                f.write(js_code)
                temp_file_path = f.name
            try:
                import subprocess

                # 使用 Node.js 执行临时文件
                result = subprocess.run(
                    ["node", temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                output = result.stdout
                data = json.loads(output)
                return data
            except subprocess.CalledProcessError as e:
                error_msg = "Node.js 执行失败，可能未安装 Node.js ，安装请访问 https://nodejs.org/"
                self.logger.error(f"{error_msg}\n{e.output}")
                self.status.append(f"{error_msg}\n{e.output}")
                return None
            except Exception as e:
                self.logger.error(f"Error executing fallback JS parser: {e}")
                self.status.append(f"Error executing fallback JS parser: {e}")
                return None

        if not self.is_logged_in:
            self.logger.warning("Not logged in. Cannot get courses info.")
            self.status.append("Not logged in. Cannot get courses info.")
            return None
        self.get_course_selection_page()
        url = f"https://eams.shanghaitech.edu.cn/eams/stdElectCourse!data.action?profileId={self.semester_id}"
        response = self.session.get(url, cookies=self.cookies)
        if response.status_code == 200:
            self.logger.info("Courses info accessed successfully.")
            self.status.append("Courses info accessed successfully.")

            try:
                data = js_var_to_py(response.text)
            except Exception as e:
                self.logger.warning(
                    f"Standard parsing failed, trying fallback method: {e}"
                )
                self.status.append(
                    f"Standard parsing failed, trying fallback method: {e}"
                )
                data = ParseFaultCallback(response.text)
                if data is None:
                    self.logger.error("Fallback parsing also failed.")
                    self.status.append("Fallback parsing also failed.")
                    return None

            assert data is not None, "Failed to parse course data."

            self.courses_info = data

            if save_to_path:
                with open(save_to_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.logger.info(f"Courses info saved to {save_to_path}")
                self.status.append(f"Courses info saved to {save_to_path}")

            return data

        else:
            self.logger.error("Failed to access courses info.")
            self.status.append("Failed to access courses info.")
            return None

    def get_all_courses(self):
        if self.courses_info is None:
            self._get_courses_info()

        return self.courses_info

    def validate_session(self) -> bool:
        student_info_url = "https://eams.shanghaitech.edu.cn/eams/stdDetail.action"
        response = self.session.get(student_info_url, cookies=self.cookies)
        if "姓名" in response.text and "性别" in response.text:
            return True
        if response.status_code != 200 or "登录" in response.text:
            print("Session expired. Please log in again.")
            self.status.append("Session expired. Please log in again.")
            self.is_logged_in = False
            return False
        return True

    def close(self):
        self.logger.info("Closing session.")
        self.is_logged_in = False
        self.login_attempts = 0
        self.session.close()

    def auto_select(self):
        if not self.is_logged_in:
            self.logger.warning("Not logged in. Cannot start auto-selection.")
            self.status.append("Not logged in. Cannot start auto-selection.")
            return
        # if not self.validate_session():
        #     self.logger.warning("Session expired. re-logining...")
        #     self.status.append("Session expired. re-logining...")
        #     self.login(self.username, self.password)
        self.stop_event.clear()
        if not self.semester_id:
            self.semester_id = self._get_semester_id()
        thread_local_data = {
            "cookies": self.cookies.copy(),
        }
        thread_select = threading.Thread(
            target=self._auto_select_thread, args=(thread_local_data,)
        )
        thread_select.start()

        return thread_select

    def _auto_select_thread(self, thread_local_data: dict):
        try:
            self.thread_lock.acquire()
            self.schedule.remove_passed_time()

            while not self.stop_event.is_set():
                remaining_seconds = self.schedule.get_remaining_seconds()
                if remaining_seconds is not None:
                    if remaining_seconds > 90:
                        if remaining_seconds % 3600 == 0:
                            self.logger.info(
                                f"Remaining time: {int(remaining_seconds)} seconds"
                            )
                            self.status.append(
                                f"Remaining time: {int(remaining_seconds)} seconds"
                            )
                            if not self.validate_session() or not self.is_logged_in:
                                self.logger.warning("Session expired. re-logining...")
                                self.status.append("Session expired. re-logining...")
                                self.login()
                        threading.Event().wait(10)
                    elif 15 < remaining_seconds <= 90:
                        if not self.validate_session() or not self.is_logged_in:
                            self.logger.warning("Session expired. re-logining...")
                            self.status.append("Session expired. re-logining...")
                            self.login()
                        if int(remaining_seconds) % 5 == 0:
                            self.logger.info(
                                f"Remaining time: {int(remaining_seconds)} seconds"
                            )
                            self.status.append(
                                f"Remaining time: {int(remaining_seconds)} seconds"
                            )
                            threading.Event().wait(1)
                    elif -self.give_up_seconds <= remaining_seconds <= 15:
                        for course_id in self.schedule.schedule:
                            self._select_course(course_id)
                            if self.stop_event.is_set():
                                break
                    else:
                        self.schedule.remove_passed_time()
                else:
                    self.logger.info(
                        "No upcoming schedule. Course selection completed."
                    )
                    self.status.append(
                        "No upcoming schedule. Course selection completed."
                    )
                    break
                if self.stop_event.wait(
                    self.auto_select_cd + random.uniform(-0.1, 0.1)
                ):
                    self.logger.info("Auto-selection stopped.")
                    self.status.append("Auto-selection stopped.")
                    break
                # threading.Event().wait(self.auto_select_cd)
        finally:
            if self.thread_lock.locked():
                self.thread_lock.release()
            self.logger.info("Auto-selection thread finished.")

    def stop_auto_select(self):
        self.stop_event.set()

    def _select_course(self, course_id: str):
        post_url = (
            f"https://eams.shanghaitech.edu.cn/eams/stdElectCourse!batchOperator.action?profileId={self.semester_id}"
            if self.semester_id
            else ""
        )
        if not post_url:
            self.logger.warning("No semester ID available. Cannot select course.")
            self.status.append("No semester ID available. Cannot select course.")
            return
        data = {'optype': 'true', 'operator0': (course_id) + ':true:0'}

        self.logger.info(f"Selecting course with ID: {course_id}")
        self.status.append(f"Selecting course with ID: {course_id}")

        response = self.session.post(
            url=post_url,
            headers=self.headers,
            cookies=self.cookies,
            data=data,
        )
        if response.status_code == 200:
            import bs4

            soup = bs4.BeautifulSoup(response.text, 'lxml')
            try:
                success_text = soup.select('td>div')
                frequently_requested_text = soup.select('div span')
            except:
                self.logger.error(soup.text)
            if len(frequently_requested_text) > 0 or "过快点击" in response.text:
                self.logger.info(frequently_requested_text[1].get_text())
                self.status.append(frequently_requested_text[1].get_text())
                self.stop_event.wait(self.auto_select_cd + random.uniform(-0.1, 0.1))
            elif len(success_text) > 0:
                self.logger.info(
                    f'\n{course_id} 已选择!'
                    + success_text[0].get_text().replace(' ', '')
                )
                self.status.append(
                    f'\n{course_id} 已选择!'
                    + success_text[0].get_text().replace(' ', '')
                )
                if not "失败" in success_text[0].get_text():
                    self.schedule.remove_schedule(course_id)
        else:
            self.logger.error(f"Post failed with status code: {response.status_code}")
            self.status.append(f"Post failed with status code: {response.status_code}")


if __name__ == "__main__":
    import signal

    # Example usage
    backend = Backends()

    # def signal_handler(signum, frame):
    #     print("Signal handler called with signal:", signum)
    #     backend.stop_auto_select()
    #     backend.close()
    #     exit(0)

    # signal.signal(signal.SIGINT, signal_handler)
    backend.load_user_info_from_file()
    # backend.login("USERNAME", "PASSWORD")
    # backend.get_eams_home()
    # backend.get_student_info()

    # backend.schedule.add_schedule("59002")
    # backend.schedule.add_schedule_time(datetime.now() + timedelta(seconds=12))
    # backend.get_course_selection_page()
    # backend.auto_select()

    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("Stopping...")
    #     signal_handler(None, None)
    # page =
    # print(page)
    courses = backend._get_courses_info()
    print(courses)
    backend.close()
