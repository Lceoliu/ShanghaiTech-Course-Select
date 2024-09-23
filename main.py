import random, os
from time import sleep
from post_method import EleceCourse
from bs4 import BeautifulSoup as bs

ElectedLessons = [49620]
import time, datetime

# 设置选课时间
# 格式为"年-月-日 时:分" e.g. "2021-09-06 20:00"
set_time = [
    "2024-07-25 20:00",
    "2024-07-26 00:00",
    "2024-07-26 08:00",
    "2024-07-26 12:00",
    "2024-07-26 16:00",
    "2024-07-26 20:00",
    "2024-07-27 00:00",
    "2024-07-27 08:00",
    "2024-07-27 12:00",
]
os.system("cls")
try:
    res = EleceCourse(ElectedLessons[0])
except Exception as e:
    print(e)
    print("请检查网络连接或者是否已经登录")
    exit()
os.system("cls")
while True:
    now_time = datetime.datetime.now()
    s_time = datetime.datetime.strptime(set_time[0], "%Y-%m-%d %H:%M")
    rest_time = (s_time - now_time).total_seconds()
    print(f"还有{rest_time}s", end='   ')
    if rest_time < -100:
        set_time.pop(0)
        if len(set_time) == 0:
            break
    elif -100 <= rest_time <= 25:
        for lesson in ElectedLessons:
            res = EleceCourse(lesson)
            bs1 = bs(res.text, 'lxml')
            # print(res.text)
            try:
                success_text = bs1.select('td>div')
                await_text = bs1.select('div span')
            except:
                print(bs1.text)
            if len(await_text) > 0:
                print(await_text[1].get_text())
            elif len(success_text) > 0:
                print(
                    f'\n{lesson}已选择!' + success_text[0].get_text().replace(' ', '')
                )
                if not "失败" in success_text[0].get_text():
                    ElectedLessons.remove(lesson)
            sleep(0.26 + random.randint(-5, 5) / 100.0)
    elif 120 > rest_time > 25:
        print("\b\b\b.", end='')
        sleep(1)
    elif rest_time >= 120:
        print("\b\b\b.", end='')
        sleep(1)
        print(".", end='')
        sleep(1)
        print(".", end='')
        sleep(1)
    if len(ElectedLessons) == 0:
        break
    print("\r", end='')
print("\n选课结束")
