# -*- coding: utf-8 -*-
# @Time    : 2025/05/22
# @Author  : Chang
import sys
import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from functools import lru_cache
from .encryption import LoginEncryptModel
from .schedule import ScheduleAutoSelector
from .my_utils import *
import requests
import random
import time
import threading
import logging
import json


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
        self.relogin_cooldown_seconds: float = 3.0
        self._last_relogin_ts: float = 0.0
        self._last_session_check_ts: float = 0.0
        self._relogin_lock = threading.Lock()
        self.last_login_response_status: Optional[int] = None
        self.last_login_response_url: str = ""
        self.last_login_response_text: str = ""

        self.courses_info: List[Dict] = None
        self.student_info = None

        self.give_up_seconds: int = 30
        self.schedule = ScheduleAutoSelector(delay_seconds=self.give_up_seconds)
        self.auto_select_cd: float = (
            0.35  # 抢课间隔时间default，会自动使用 auto_check_anti_mechanism_cooldown 方法检测并调整到最优值
        )

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

        # 每次登录都重置状态，避免旧重试计数导致后续 relogin 直接失败
        self.login_attempts = 0
        self.need_captcha = False
        self.is_logged_in = False

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
        while not self.is_logged_in and self.login_attempts < self.login_max_retries:
            try:
                first_response = self.session.get(
                    self.auth_url, cookies=self.cookies, timeout=10
                )
            except requests.RequestException as e:
                self.login_attempts += 1
                self.logger.error(f"Error requesting login page: {e}")
                self.status.append(f"Error requesting login page: {e}")
                self.stop_event.wait(min(1.5 * self.login_attempts, 5))
                continue

            if not self._parse_login_page(first_response.text):
                # 已经存在 SSO 登录态时，auth_url 可能直接跳转业务页而非返回登录表单
                if "authserver/login" not in (first_response.url or ""):
                    if self.validate_session():
                        self.logger.info(
                            "Existing authenticated session detected; login form not required."
                        )
                        self.status.append(
                            "Existing authenticated session detected; login form not required."
                        )
                        self.is_logged_in = True
                        break

                    # 登录态不一致：清理 SSO 相关 cookie，强制下次尝试拿到登录表单
                    self._clear_sso_cookies()
                self.login_attempts += 1
                self.logger.error(
                    "Failed to parse login page tokens (pwdEncryptSalt/execution)."
                )
                self.status.append(
                    "Failed to parse login page tokens (pwdEncryptSalt/execution)."
                )
                self.stop_event.wait(min(1.5 * self.login_attempts, 5))
                continue

            try:
                captcha_response = self.session.get(
                    f"https://ids.shanghaitech.edu.cn/authserver/checkNeedCaptcha.htl?username={username}&_={int(time.time()*1000)}",
                    timeout=10,
                )
            except requests.RequestException as e:
                self.login_attempts += 1
                self.logger.error(f"Error checking captcha: {e}")
                self.status.append(f"Error checking captcha: {e}")
                self.stop_event.wait(min(1.5 * self.login_attempts, 5))
                continue

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
                self.stop_event.wait(min(1.5 * self.login_attempts, 5))
        if not self.is_logged_in:
            self.logger.warning("Login attempts exceeded maximum retries.")
            self.status.append("Login attempts exceeded maximum retries.")
        else:
            self.login_attempts = 0  # reset attempts after successful login
        return self.is_logged_in

    def _clear_sso_cookies(self) -> None:
        for cookie in list(self.session.cookies):
            domain = (cookie.domain or "").lower()
            if (
                "ids.shanghaitech.edu.cn" in domain
                or "egate-new.shanghaitech.edu.cn" in domain
            ):
                self.session.cookies.clear(
                    domain=cookie.domain, path=cookie.path, name=cookie.name
                )

    def _parse_login_page(self, html: str) -> bool:
        import bs4

        res = bs4.BeautifulSoup(html, 'lxml')
        salt_element = res.select_one("#pwdEncryptSalt")
        execution_element = res.select_one("#execution")
        if not salt_element or not execution_element:
            return False
        salt = salt_element.get('value', '')
        execution = execution_element.get('value', '')
        if not salt or not execution:
            return False

        self.encrypt_model.set_salt(salt)
        if self.data:
            self.data['execution'] = execution
        else:
            raise ValueError("Data is not set.")
        return True

    def _append_wrong_password_status_if_present(self, text: str) -> None:
        if "您提供的用户名或者密码有误" in (text or ""):
            self.logger.error("您提供的用户名或者密码有误")
            self.status.append("您提供的用户名或者密码有误")

    def _get_captcha_code(self):
        # This method should implement the logic to get the captcha code from the user
        # For now, we will just return a dummy value
        return "dummy_captcha"

    def _submit_login(self, captcha_code=None) -> bool:
        if captcha_code:
            self.data['captcha'] = captcha_code

        encrypted_password = self.encrypt_model.encrypt_password(self.password)
        self.data['password'] = encrypted_password

        try:
            response = self.session.post(
                self.auth_url,
                data=self.data,
                timeout=10,
            )
        except requests.RequestException as e:
            self.logger.error(f"Login request failed: {e}")
            self.status.append(f"Login request failed: {e}")
            self.is_logged_in = False
            return False
        self.last_login_response_status = response.status_code
        self.last_login_response_url = response.url
        self.last_login_response_text = response.text or ""
        self.session.cookies.update(response.cookies)
        if response.status_code != 200:
            self.logger.error(f"Login failed! status_code={response.status_code}")
            self.status.append(f"Login failed! status_code={response.status_code}")
            self._append_wrong_password_status_if_present(self.last_login_response_text)
            self.is_logged_in = False
            return False

        # 真实结果确认：用受保护资源验证会话是否有效，避免依赖不稳定页面文案特征
        self.is_logged_in = self.validate_session()
        if self.is_logged_in:
            self.logger.info("Login successful!")
            self.status.append("Login successful!")
            return True

        self.logger.error("Login failed! session is still invalid after submit.")
        self.status.append("Login failed! session is still invalid after submit.")
        self._append_wrong_password_status_if_present(self.last_login_response_text)
        return False

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

    @lru_cache(maxsize=1)
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

        if "未到选课时间" in response.text:
            print("Not in course selection period.")
            self.status.append("Not in course selection period.")
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
        if self.semester_id is None:
            self.logger.error("Semester ID is not set. Cannot get courses info.")
            self.status.append("Semester ID is not set. Cannot get courses info.")
            return None
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

    def auto_check_anti_mechanism_cooldown(self):
        """
        自动检查触发“请不要过快点击”机制的最短请求间隔，以达成最佳抢课节奏。
        """
        self.logger.info("正在测试当前网络环境下触发反爬机制的最短请求间隔...")
        self.status.append("正在测试当前网络环境下触发反爬机制的最短请求间隔...")
        student_info_url = "https://eams.shanghaitech.edu.cn/eams/stdDetail.action"
        cool_down_min = 250  # 最小间隔 250ms
        cool_down_max = 550  # 最大间隔 550ms
        cool_down_step = 50  # 每次增加50ms
        current_cd = cool_down_min
        retry_every_cd = 5  # 每个间隔尝试5次，majority vote 判定是否触发机制
        results = {}  # {cd: successful tries ratio}
        cnt_for_cd = 0
        while current_cd <= cool_down_max:
            student_info_url = "https://eams.shanghaitech.edu.cn/eams/stdDetail.action"

            response = self.session.get(
                student_info_url, cookies=self.cookies, timeout=10
            )

            if response.status_code != 200 or "登录" in response.text:
                break
            if "姓名" in response.text and "性别" in response.text:
                results[current_cd] = (
                    results.get(current_cd, 0) * (cnt_for_cd) + 1
                ) / (cnt_for_cd + 1)
                print(f"间隔 {current_cd} ms: 成功访问学生信息页面，未触发反爬机制。")
            if "过快点击" in response.text:
                results[current_cd] = (
                    results.get(current_cd, 0) * (cnt_for_cd) + 0
                ) / (cnt_for_cd + 1)
                print(f"间隔 {current_cd} ms: 触发了过快点击的反爬机制。")

            time.sleep(current_cd / 1000)  # 转换为秒
            cnt_for_cd += 1
            if cnt_for_cd >= retry_every_cd:
                current_cd += cool_down_step
                cnt_for_cd = 0
                time.sleep(
                    cool_down_step / 1000
                )  # 每次增加间隔后额外等待一次，避免连续请求导致状态被互相覆盖
        self.logger.info(f"Anti-mechanism cooldown check results: {results}")
        min_possible_cd = min(
            cd for cd, ratio in results.items() if ratio >= 0.8
        )  # 取成功率大于等于80%的最小间隔作为估计的最短安全间隔
        self.logger.info(f"Estimated minimum possible cooldown: {min_possible_cd} ms")
        self.status.append(f"Estimated minimum possible cooldown: {min_possible_cd} ms")

    def validate_session(self) -> bool:
        student_info_url = "https://eams.shanghaitech.edu.cn/eams/stdDetail.action"
        try:
            response = self.session.get(
                student_info_url, cookies=self.cookies, timeout=10
            )
        except requests.RequestException as e:
            self.logger.warning(f"Session check failed due to network error: {e}")
            self.status.append(f"Session check failed due to network error: {e}")
            self.is_logged_in = False
            return False
        if response.status_code != 200 or "登录" in response.text:
            print("Session expired. Please log in again.")
            self.status.append("Session expired. Please log in again.")
            self.is_logged_in = False
            return False
        if "姓名" in response.text and "性别" in response.text:
            self.is_logged_in = True
            return True
        if "过快点击" in response.text:
            self.logger.warning("过快点击导致的反爬机制触发，暂不强制登出，继续尝试。")
            return True  # 反爬机制触发时不强制登出，给用户提示并继续尝试
        self.logger.warning(
            f"Session validation failed: unexpected response. Response texts: {response.text.strip()[:4000]}..."
        )
        self.status.append(
            "Session validation failed: unexpected response. Check logs for details."
        )
        self.is_logged_in = False
        return False

    def ensure_login(self):
        now = time.time()
        if now - self.last_login_attempt < self.login_cooldown:
            return
        if not self.login_lock.acquire(blocking=False):
            return
        try:
            if self.is_logged_in and self.validate_session():
                return
            self.last_login_attempt = now
            self.login()
        finally:
            self.login_lock.release()

    def _maybe_relogin(self, force: bool = False) -> bool:
        if self.username is None or self.password is None:
            self.logger.warning("No cached credentials. Cannot relogin automatically.")
            self.status.append("No cached credentials. Cannot relogin automatically.")
            return False

        now = time.monotonic()
        if not force and now - self._last_relogin_ts < self.relogin_cooldown_seconds:
            return False

        if not self._relogin_lock.acquire(blocking=False):
            return False
        try:
            self._last_relogin_ts = time.monotonic()
            self.logger.warning("Session expired. re-logining...")
            self.status.append("Session expired. re-logining...")
            try:
                return bool(self.login())
            except Exception as e:
                self.logger.error(f"Relogin failed with exception: {e}")
                self.status.append(f"Relogin failed with exception: {e}")
                self.is_logged_in = False
                return False
        finally:
            self._relogin_lock.release()

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
        self.stop_event.clear()
        self.auto_select_cd = self.auto_check_anti_mechanism_cooldown()
        if not self.semester_id:
            self.semester_id = self._get_semester_id()
            self.logger.info(f"Semester ID: {self.semester_id}")
            self.status.append(f"Semester ID: {self.semester_id}")
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
                        now = time.monotonic()
                        # 长等待阶段按固定间隔检查会话，避免 session 过期后直到临近触发才发现
                        if now - self._last_session_check_ts >= 30:
                            self._last_session_check_ts = now
                            if not self.validate_session() or not self.is_logged_in:
                                self._maybe_relogin()
                        if int(remaining_seconds) % 3600 == 0:
                            self.logger.info(
                                f"Remaining time: {int(remaining_seconds)} seconds"
                            )
                            self.status.append(
                                f"Remaining time: {int(remaining_seconds)} seconds"
                            )
                        if self.stop_event.wait(10):
                            break
                    elif 15 < remaining_seconds <= 90:
                        now = time.monotonic()
                        if now - self._last_session_check_ts >= 5:
                            self._last_session_check_ts = now
                            if not self.validate_session() or not self.is_logged_in:
                                self._maybe_relogin(force=True)
                        if not self.validate_session() or not self.is_logged_in:
                            # 登录失败时短暂退避，避免连续刷登录导致状态被互相覆盖
                            self.stop_event.wait(2.0)
                            continue
                        if int(remaining_seconds) % 5 == 0:
                            self.logger.info(
                                f"Remaining time: {int(remaining_seconds)} seconds"
                            )
                            self.status.append(
                                f"Remaining time: {int(remaining_seconds)} seconds"
                            )
                            if self.stop_event.wait(1):
                                break
                    elif -self.give_up_seconds <= remaining_seconds <= 15:
                        if not self.validate_session() or not self.is_logged_in:
                            if not self._maybe_relogin(force=True):
                                self.stop_event.wait(1.5)
                                continue
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
        # 如果要退课，则是 {'optype': 'false', 'operator0': (course_id) + ':false'}

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
                # 触发过快点击机制时短暂退避，可以有效减少触发机制的概率，提升成功率
                self.stop_event.wait(self.auto_select_cd + random.uniform(0, 0.25))
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
    backend.login()
    # backend.login("USERNAME", "PASSWORD")
    backend.get_eams_home()
    backend.get_student_info()
    # backend.validate_session()
    backend.auto_check_anti_mechanism_cooldown()

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
