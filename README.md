## 项目介绍

上海科技大学自动抢课程序

运气不好怎么办？这个程序可以帮你蹲守允许抢课的时间段，~~截胡别人的交易~~

## 目录结构

目前最新的有效部分如下：

```bash
├── main.py
├── README.md
├── Backends.py
├── FrontUI.py
├── user_info.secret
```

## 环境配置

1. My Python Version = 3.11.5 (仅供参考)
2. pip install -r ./requirements.txt
3. ~~配置 selenium 环境 (使用了 google chrome)~~

## 使用指南

### 使用 CLI

1. 在 user_info.secret 中配置你的账号密码

2. 通过命令行运行
   ```bash
   python main.py --id="59002" "59003" --time="2025-05-24 02:00" "2025-05-24 04:00"
   ```

### 使用 GUI

1. 目前由于暂未 build GUI，所以只能在本地配置 flet 库环境

2. 直接运行
   ```bash
   python main.py
   ```
