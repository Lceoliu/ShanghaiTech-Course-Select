## 项目简介

上海科技大学自动抢课程序

运气不好怎么办？这个程序可以帮你蹲守允许抢课的时间段，~~截胡别人的交易~~

## 目录结构

```bash
.
├── course_auto_select/
│   ├── __init__.py          # 对外导出 Backends、CLI、GUI
│   ├── __main__.py          # 支持 `python -m course_auto_select`
│   ├── cli.py               # 命令行入口与参数解析
│   ├── ui.py                # Flet GUI（可选）
│   └── backends/
│       ├── __init__.py
│       ├── core.py          # 会话、抢课、日志核心
│       ├── encryption.py    # 登录口令加密
│       └── schedule.py      # 触发时间与课程队列
├── Backends.py              # 兼容旧引用，内部 re-export
├── FrontUI.py               # 兼容旧引用，内部 re-export
├── main.py                  # 兼容旧 `python main.py`
├── requirements.txt         # 运行依赖
├── user_info.secret         # 用户配置示例
└── tests/                   # 轻量自检脚本
```

冗余脚本（爬虫、暴力破解等）已经清理，仓库只保留直接为主流程服务的代码。

## 安装与依赖

1. Python 3.11（推荐）
2. `pip install -r requirements.txt`

依赖仅包含请求、Flet、以及加密所需的 `pycryptodome`。

## 使用说明

### 配置账号

在 `user_info.secret` 写入：

```ini
[user_info]
username = your_id
password = your_password
```

### 获取当前学期所有课程 ID
运行 `get_courses.py` 脚本，保存课程信息到 `courses.json`：

```bash
python get_courses.py --config user_info.secret
```

### CLI 模式

```bash
python -m course_auto_select --id 59002 59003 --time "2025-05-24 02:00" "2025-05-24 04:00"
```

- `--id` 支持多个课程 ID。
- `--time` 支持多个触发时间，格式固定为 `YYYY-MM-DD HH:MM`。
- `--config` 可选，指定其它凭据文件。

### GUI 模式

```bash
python -m course_auto_select
```

若未给定 `--id/--time`，CLI 会自动拉起 Flet GUI。

### 运行日志

日志默认写入 `logs/backend_*.log`。在 GUI 界面或命令行输出也能看到简要状态。

## 维护建议

- 新增功能时优先放入 `course_auto_select/` 包内，保持根目录整洁。
- 如果扩展了后端能力，请补充最小化的自检脚本至 `tests/`。
- 如需样例课程数据，可自行抓取保存到 `courses.json`，仓库不再提供冗长示例。
