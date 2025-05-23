import datetime
import flet as ft
from Backends import Backends


class FrontWindow:
    def __init__(self, backend: Backends):
        self.backend = backend

        self.page = None
        self.username_field = None
        self.password_field = None
        self.login_progress = None
        self.login_message = None
        self.student_info = None
        self.tabs = None
        self.current_tab = None

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("课程号")),
                ft.DataColumn(ft.Text("课程名称")),
                ft.DataColumn(ft.Text("课程代码")),
                ft.DataColumn(ft.Text("学分")),
                ft.DataColumn(ft.Text("授课教师")),
                ft.DataColumn(ft.Text("操作")),
            ],
            rows=[],
        )
        self.plan_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("课程号")),
                ft.DataColumn(ft.Text("课程名称")),
                ft.DataColumn(ft.Text("课程代码")),
                ft.DataColumn(ft.Text("授课教师")),
                ft.DataColumn(ft.Text("操作")),
            ],
            rows=[],
        )

        self.scheduled_time_list = []  # 存储抢课时间列表
        self.schedule_timelist_text = ft.TextField(
            label="选择时间",
            hint_text="选择抢课时间",
            width=200,
            border_radius=8,
            icon=ft.Icons.DATE_RANGE,
            multiline=True,
            min_lines=1,
            max_lines=3,
        )
        self.scheduled_course_ids = []
        self.all_courses = []  # 存储所有课程数据用于搜索
        self.matched_search_results = []  # 存储搜索匹配结果
        self.searchbar = None

        self.app = ft.app(self.main, name="Course Selection")

    def create_window_elements(self):
        # 创建界面元素
        self.username_field = ft.TextField(
            label="用户名",
            autofocus=True,
            prefix_icon=ft.icons.PERSON,
            border_radius=8,
        )

        self.password_field = ft.TextField(
            label="密码",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.LOCK_OUTLINE,
            border_radius=8,
        )

        self.login_progress = ft.ProgressBar(visible=False)
        self.login_message = ft.Text(visible=False, size=14)

        # 创建Tab页
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="课程列表", icon=ft.icons.BOOK),
                ft.Tab(text="抢课计划", icon=ft.icons.BOOKMARK),
                ft.Tab(text="个人设置", icon=ft.icons.SETTINGS),
            ],
        )

    def handle_login(self, e):
        username = self.username_field.value
        password = self.password_field.value

        if not username or not password:
            self.show_login_message("请输入用户名和密码", ft.colors.RED)
            return

        self.login_progress.visible = True
        self.page.update()

        # 执行登录
        try:
            self.backend.login(username, password)

            if self.backend.is_logged_in:
                self.show_login_message("登录成功！正在加载...", ft.colors.GREEN)
                # 使用动画过渡到主界面
                self.page.splash = ft.ProgressBar()
                self.page.update()

                # 获取学生信息
                self.student_info = self.backend.get_student_info()

                # 显示主界面
                self.show_main_interface()
            else:
                error_message = "登录失败"
                if (
                    self.backend.status
                    and "用户名或者密码有误" in self.backend.status[-1]
                ):
                    error_message = "用户名或密码错误，请重试"
                self.show_login_message(error_message, ft.colors.RED)
                self.login_progress.visible = False
                self.page.update()
        except Exception as e:
            self.show_login_message(f"登录过程中发生错误: {str(e)}", ft.colors.RED)
            self.login_progress.visible = False
            self.page.update()

    def show_login_message(self, message, color):
        self.login_message.value = message
        self.login_message.color = color
        self.login_message.visible = True
        self.page.update()

    def show_login_page(self, page: ft.Page = None):
        if page is None:
            page = self.page

        page.title = "登录 - 课程选择系统"
        page.clean()

        # 创建登录界面元素如果尚未创建
        if self.username_field is None:
            self.create_window_elements()

        # 登录按钮
        login_button = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.icons.LOGIN), ft.Text("登录", size=16)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=200,
            on_click=self.handle_login,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=5,
            ),
        )

        # 登录表单
        login_form = ft.Container(
            content=ft.Column(
                [
                    ft.Text("课程选择系统", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("请使用学校账号登录", size=16, opacity=0.8),
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    self.username_field,
                    self.password_field,
                    self.login_message,
                    ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                    self.login_progress,
                    ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                    login_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            width=400,
            padding=30,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLACK12,
                offset=ft.Offset(0, 5),
            ),
        )

        # 登录页布局
        login_layout = ft.Column(
            [login_form],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        page.add(
            ft.Container(
                content=login_layout,
                expand=True,
                alignment=ft.alignment.center,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.colors.BLUE_50, ft.colors.INDIGO_50],
                ),
            )
        )

        # 设置响应式布局
        page.on_resize = self.on_page_resize
        page.update()

    def on_page_resize(self, e):
        # 保持响应式设计
        self.page.update()

    def on_search_change(self, e):
        """当搜索框内容变化时更新搜索结果"""
        search_term = e.control.value.lower()
        if not search_term or search_term == "":
            self.searchbar.controls = []
            self.page.update()
            return

        # 搜索所有课程
        matched_courses = []
        for course in self.all_courses:
            if (
                search_term in course.get('name', '').lower()
                or search_term in course.get('code', '').lower()
                or search_term in course.get('no', '').lower()
            ):
                matched_courses.append(course)
        self.searchbar.controls.clear()
        for course in matched_courses:
            self.searchbar.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{course.get('name')} ({course.get('code')})"),
                    data=course,
                    on_click=lambda e: self.on_search_result_tap(e),
                )
            )

        self.update_course_table(matched_courses)
        self.page.update()

    def on_search_submit(self, e):
        """当用户提交搜索时过滤表格"""
        search_term: str = e.control.value.lower()
        if not search_term or search_term == "" or search_term == "*":
            # 显示所有课程
            self.update_course_table(self.all_courses)
            return

        # 过滤符合条件的课程
        filtered_courses = []
        for course in self.all_courses:
            if (
                search_term in course.get('name', '').lower()
                or search_term in course.get('code', '').lower()
                or search_term in course.get('no', '').lower()
            ):
                filtered_courses.append(course)

        # 更新表格显示过滤后的结果
        self.update_course_table(filtered_courses)
        self.page.open(ft.SnackBar(ft.Text(f"找到 {len(filtered_courses)} 个匹配结果")))

    def on_search_result_tap(self, e):
        """处理搜索结果点击事件"""
        selected_course = e.control.data

        self.update_course_table([selected_course])

        self.searchbar.controls = []
        self.page.update()

    def show_main_interface(self):
        self.page.splash = None
        self.page.title = "课程选择系统"
        self.page.clean()

        # 获取学生姓名和其他信息
        student_name = "用户"
        grade = ""
        major = ""
        if self.student_info:
            if "student_name" in self.student_info:
                student_name = self.student_info["student_name"]
            if "grade" in self.student_info:
                grade = self.student_info["grade"]
            if "major" in self.student_info:
                major = self.student_info["major"]
        try:
            app_bar = ft.AppBar(
                leading=ft.Icon(ft.icons.SCHOOL),
                leading_width=40,
                title=ft.Text("课程选择系统"),
                center_title=False,
                bgcolor=ft.colors.LIGHT_BLUE_100,
                actions=[
                    ft.PopupMenuButton(
                        icon=ft.icons.PERSON,
                        tooltip="个人信息",
                        items=[
                            ft.PopupMenuItem(
                                text=f"姓名: {student_name}",
                                mouse_cursor=ft.MouseCursor.BASIC,
                            ),
                            ft.PopupMenuItem(
                                text=f"年级: {grade}", mouse_cursor=ft.MouseCursor.BASIC
                            ),
                            ft.PopupMenuItem(
                                text=f"专业: {major}", mouse_cursor=ft.MouseCursor.BASIC
                            ),
                            ft.PopupMenuItem(icon=ft.Icons.HORIZONTAL_RULE),
                            ft.PopupMenuItem(
                                text="退出登录",
                                icon=ft.icons.LOGOUT,
                                on_click=self.logout,
                            ),
                        ],
                        padding=5,
                    ),
                    ft.Text(student_name, size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(width=20),
                ],
            )

            def on_tab_searchbar(e):
                assert isinstance(
                    e.control, ft.SearchBar
                ), f'{e.control} is not a SearchBar'
                # e.control.open_view()
                self.on_search_change(e)
                # e.control.update()

            self.searchbar = ft.SearchBar(
                width=220,
                divider_color=ft.Colors.GREY_200,
                bar_hint_text="搜索课程、课程代码",
                view_hint_text="搜索课程、课程代码",
                on_change=self.on_search_change,
                on_submit=self.on_search_submit,
                on_tap=on_tab_searchbar,
                controls=[],
            )

            course_list_content = ft.Column(
                [
                    ft.Text("课程列表", size=24, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "从JSON文件导入课程",
                                icon=ft.icons.FILE_OPEN,
                                on_click=self.show_course_infos,
                            ),
                            ft.ElevatedButton(
                                "刷新课程列表",
                                icon=ft.icons.REFRESH,
                                on_click=lambda e: self.update_course_table(
                                    self.backend.get_all_courses()
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10,
                    ),
                    ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                    ft.Row([ft.Text("课程信息", size=20), self.searchbar]),
                    ft.Column(
                        [
                            ft.Container(
                                content=self.data_table,
                                padding=10,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=8,
                            ),
                        ],
                        height=min(max(80, self.page.height - 300), 400),
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                expand=True,
                spacing=15,
            )
            course_id_text = ft.TextField(
                label="课程代码",
                hint_text="输入要抢的课程代码",
                width=200,
                border_radius=8,
            )

            # 创建抢课计划界面内容
            course_plan_content = ft.Column(
                [
                    ft.Text("抢课计划", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("创建抢课计划", size=18),
                                ft.Row(
                                    [
                                        course_id_text,
                                        ft.ElevatedButton(
                                            "添加",
                                            icon=ft.icons.ADD,
                                            on_click=lambda e: self.add_course_to_plan(
                                                course_id_text.value
                                            ),
                                        ),
                                        ft.ElevatedButton(
                                            "开始抢课",
                                            icon=ft.icons.PLAY_ARROW,
                                            on_click=lambda e: self.start_electing(),
                                        ),
                                        ft.ElevatedButton(
                                            "停止抢课",
                                            icon=ft.icons.STOP,
                                            on_click=lambda e: self.stop_electing(),
                                        ),
                                        ft.Container(
                                            content=ft.Row(
                                                [
                                                    self.schedule_timelist_text,
                                                    ft.ElevatedButton(
                                                        "添加时间",
                                                        icon=ft.icons.ADD,
                                                        on_click=lambda e: self.open_time_picker(
                                                            e
                                                        ),
                                                    ),
                                                    ft.ElevatedButton(
                                                        "清除时间",
                                                        icon=ft.icons.CLEAR,
                                                        on_click=lambda e: self.clear_time_list(),
                                                    ),
                                                ]
                                            ),
                                            width=500,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    spacing=10,
                                ),
                                ft.Divider(),
                                ft.Text("已添加的抢课计划", size=18),
                                self.plan_table,
                            ],
                            spacing=15,
                        ),
                        padding=20,
                        border=ft.border.all(1, ft.colors.OUTLINE),
                        border_radius=8,
                    ),
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
            )

            # 创建个人设置界面内容
            settings_content = ft.Column(
                [
                    ft.Text("个人设置", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("账号信息", size=18),
                                ft.ListTile(
                                    leading=ft.Icon(ft.icons.PERSON),
                                    title=ft.Text("用户名"),
                                    subtitle=ft.Text(student_name),
                                ),
                                ft.ListTile(
                                    leading=ft.Icon(ft.icons.SCHOOL),
                                    title=ft.Text("年级"),
                                    subtitle=ft.Text(grade),
                                ),
                                ft.ListTile(
                                    leading=ft.Icon(ft.icons.BOOK),
                                    title=ft.Text("专业"),
                                    subtitle=ft.Text(major),
                                ),
                                ft.Divider(),
                                ft.Text("系统设置", size=18),
                                ft.Switch(label="开启抢课提醒", value=True),
                                ft.Switch(label="显示调试信息", value=False),
                                ft.ElevatedButton(
                                    "清除缓存",
                                    icon=ft.icons.CLEANING_SERVICES,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=20,
                        border=ft.border.all(1, ft.colors.OUTLINE),
                        border_radius=8,
                    ),
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
            )

            # 创建内容区域容器 - 默认显示课程列表
            tab_content = ft.Container(
                content=course_list_content,
                expand=False,
                padding=20,
            )

            pagelet = ft.Pagelet(
                appbar=app_bar,
                content=ft.Container(
                    ft.Column(
                        [self.tabs, ft.Divider(height=1), tab_content],
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        spacing=0,
                    ),
                    margin=20,
                ),
                bgcolor=ft.colors.WHITE12,
                # expand=True,
            )

        except Exception as e:
            print(f"创建界面元素时出错: {str(e)}")
            self.page.add(
                ft.Column(
                    [
                        ft.Text("界面加载出错", size=24, color=ft.colors.RED),
                        ft.Text(f"错误信息: {str(e)}", size=16),
                        ft.ElevatedButton(
                            "返回登录", on_click=lambda _: self.show_login_page()
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
            self.page.update()
            return

        # Tab切换处理
        def on_tab_change(e):
            tab_index = e.control.selected_index
            if tab_index == 0:
                # 课程列表
                tab_content.content = course_list_content
            elif tab_index == 1:
                # 抢课计划
                tab_content.content = course_plan_content
            elif tab_index == 2:
                # 个人设置
                tab_content.content = settings_content
            self.page.update()

        self.tabs.on_change = on_tab_change

        self.page.add(pagelet)

        # 尝试加载默认课程数据
        try:
            default_courses = self.backend.get_all_courses()
            if default_courses:
                self.update_course_table(default_courses)
        except:
            # 如果默认加载失败，显示空表格即可
            pass

        self.page.update()

    def logout(self, e=None):
        # 实现登出功能
        self.backend.close()

        # 显示登出动画
        self.page.splash = ft.ProgressBar()
        self.page.update()

        # 返回登录页
        self.login_progress.visible = False
        self.login_message.visible = False
        self.password_field.value = ""
        self.show_login_page()

    def get_course_from_id(self, course_id) -> dict:
        # 根据课程ID获取课程信息
        course = next(
            (course for course in self.all_courses if course['id'] == course_id),
            None,
        )
        return course

    def start_electing(self):
        # 开始抢课
        import threading

        # 检查是否有课程和时间设置
        if not self.scheduled_course_ids:
            self.page.open(
                ft.SnackBar(ft.Text("请先添加要抢的课程！"), bgcolor=ft.colors.RED)
            )
            return

        if not self.scheduled_time_list:
            self.page.open(
                ft.SnackBar(ft.Text("请先设置抢课时间！"), bgcolor=ft.colors.RED)
            )
            return

        self.page.open(ft.SnackBar(ft.Text("抢课已开始...")))
        self.backend.schedule.clear_schedule()

        # 添加课程到抢课计划
        for course_id in self.scheduled_course_ids:
            self.backend.schedule.add_schedule(course_id)
            print(f"添加课程到抢课计划: {course_id}")

        # 添加时间到抢课计划
        for time_str in self.schedule_timelist_text.value.split("\n"):
            try:
                time_obj = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                self.backend.schedule.add_schedule_time(time_obj)
                print(f"添加时间到抢课计划: {time_str} -> {time_obj}")
            except ValueError as e:
                print(f"时间格式错误: {time_str}, 错误: {e}")
                self.page.open(
                    ft.SnackBar(
                        ft.Text(f"时间格式错误: {time_str}"), bgcolor=ft.colors.RED
                    )
                )
                return

        # 打印当前抢课计划状态
        print(f"当前抢课课程: {self.backend.schedule.schedule}")
        print(f"当前抢课时间: {self.backend.schedule.schedule_timelist}")

        # 检查剩余时间
        remaining = self.backend.schedule.get_remaining_seconds()
        if remaining is not None:
            print(f"距离下次抢课还有: {remaining} 秒")
            self.page.open(
                ft.SnackBar(ft.Text(f"距离下次抢课还有: {int(remaining)} 秒"))
            )
        else:
            print("没有即将到来的抢课时间")
            self.page.open(
                ft.SnackBar(ft.Text("没有即将到来的抢课时间"), bgcolor=ft.colors.ORANGE)
            )

        # 开始抢课线程
        as_thread: threading.Thread = self.backend.auto_select()

    def stop_electing(self):
        self.backend.stop_event.set()
        self.page.open(ft.SnackBar(ft.Text("抢课已停止")))

    def add_course_to_plan(self, course_code):
        # 添加课程到抢课计划
        all_ids = [course['id'] for course in self.all_courses]
        if course_code not in all_ids:
            self.page.open(ft.SnackBar(ft.Text(f"课程 {course_code} 不存在")))
            return
        self.scheduled_course_ids.append(course_code)
        course = self.get_course_from_id(course_code)
        if not course:
            return
        self.page.open(
            ft.SnackBar(ft.Text(f"已将课程 {course['name']} 添加到抢课计划"))
        )

        self.plan_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(course['id'])),
                    ft.DataCell(ft.Text(course['name'])),
                    ft.DataCell(ft.Text(course['code'])),
                    ft.DataCell(ft.Text(course['teachers'])),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e: self.remove_course_from_plan(
                                e, course_code
                            ),
                        )
                    ),
                ]
            )
        )
        self.page.update()

    def remove_course_from_plan(self, e, course_code):
        # 从抢课计划中移除课程
        self.scheduled_course_ids.remove(course_code)
        self.plan_table.rows = [
            row
            for row in self.plan_table.rows
            if row.cells[0].content.value != course_code
        ]
        self.page.update()

    def open_time_picker(self, e):
        # 打开时间选择器
        self.scheduled_time_list.append(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        self.schedule_timelist_text.value = "\n".join(self.scheduled_time_list)
        self.page.update()

        def handle_time_change(e: ft.ControlEvent):
            if e.control.value:
                selected_time = e.control.value.strftime('%Y-%m-%d %H:%M')
                print(f"选择的时间: {selected_time}")
                self.scheduled_time_list[-1] = selected_time
                self.schedule_timelist_text.value = "\n".join(self.scheduled_time_list)
                self.page.update()

        self.page.open(
            ft.CupertinoBottomSheet(
                ft.CupertinoDatePicker(
                    date_picker_mode=ft.CupertinoDatePickerMode.DATE_AND_TIME,
                    use_24h_format=True,
                    minute_interval=60,
                    on_change=handle_time_change,
                ),
                height=260,
                padding=ft.padding.only(top=6, bottom=6),
            )
        )

    def update_course_table(self, datas: list[dict]):
        """更新课程数据表格"""
        try:
            if not datas:
                self.data_table.rows = []
                self.page.update()
                return

            self.all_courses = self.backend.get_all_courses()
            rows = []
            for course in datas:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(course.get('id', ''))),
                            ft.DataCell(ft.Text(course.get('name', ''))),
                            ft.DataCell(ft.Text(course.get('code', ''))),
                            ft.DataCell(ft.Text(course.get('credits', ''))),
                            ft.DataCell(ft.Text(course.get('teachers', ''))),
                            ft.DataCell(
                                ft.Button(
                                    "添加",
                                    on_click=lambda e, course_id=course.get(
                                        'id', ''
                                    ): self.add_course_to_plan(course_id),
                                )
                            ),
                        ]
                    )
                )

            # self.page.open(ft.SnackBar(ft.Text("更新课程列表成功...")))
            self.data_table.rows = rows
            self.page.update()
        except Exception as e:
            self.page.open(ft.SnackBar(ft.Text(f"更新表格时出错: {str(e)}")))

    def show_course_infos(self, e=None):
        # 显示课程信息
        try:
            # 弹出文件选择对话框
            def pick_files_result(e: ft.FilePickerResultEvent):
                if e.files:
                    # 文件已选择，显示加载提示
                    self.page.open(ft.SnackBar(ft.Text("正在加载课程信息...")))

                    # 通过后端加载选择的文件
                    filepath = e.files[0].path
                    datas = self.backend.load_courses_info(filepath)

                    # 更新数据表格
                    self.update_course_table(datas)

                    # 显示成功消息
                    self.page.open(
                        ft.SnackBar(ft.Text(f"成功加载 {len(datas)} 门课程信息"))
                    )
                else:
                    # 用户取消了文件选择
                    self.page.open(ft.SnackBar(ft.Text("未选择文件")))

            # 创建文件选择器
            file_picker = ft.FilePicker(on_result=pick_files_result)
            self.page.overlay.append(file_picker)
            self.page.update()

            # 显示文件选择对话框
            file_picker.pick_files(
                allowed_extensions=["json"],
                dialog_title="选择课程信息文件",
            )
        except Exception as e:
            # 处理异常
            self.page.open(ft.SnackBar(ft.Text(f"加载课程信息出错: {str(e)}")))

    def clear_time_list(self):
        """清除时间列表"""
        self.scheduled_time_list.clear()
        self.schedule_timelist_text.value = ""
        self.page.update()
        self.page.open(ft.SnackBar(ft.Text("已清除所有时间设置")))

    def main(self, page: ft.Page):
        self.page = page
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1000
        page.window_height = 800
        page.window_min_width = 400
        page.window_min_height = 600

        # 设置主题
        page.theme = ft.Theme(
            color_scheme_seed=ft.colors.BLUE,
            primary_color=ft.colors.BLUE_500,
        )

        if not self.backend.is_logged_in:
            self.show_login_page()
        else:
            self.show_main_interface()
