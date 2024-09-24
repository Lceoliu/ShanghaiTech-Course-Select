import json
from json import JSONDecodeError

# TODO: 请在此处填写你的学期id
semester = '2444'

elect_url = f"https://eams.shanghaitech.edu.cn/eams/stdElectCourse!batchOperator.action?profileId={semester}"
course_json_uri = f"https://eams.shanghaitech.edu.cn/eams/stdElectCourse!data.action?profileId={semester}"
# https://eams.shanghaitech.edu.cn/eams/stdElectCourse!data.action?profileId=2327
home_page_url = f"https://eams.shanghaitech.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id={semester}"
# https://eams.shanghaitech.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id=2327
root_url = "https://eams.shanghaitech.edu.cn/eams/stdElectCourse.action"

headers = {
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://eams.shanghaitech.edu.cn',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

headers_courseJson = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'If-None-Match': '1704902762995_11817',
    'Referer': f'https://eams.shanghaitech.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id={semester}',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

cookies = {}
# e.g.
# 'JSESSIONID': 'AD2...B58',
# 'srv_id': '01ae...e2',
# 如果要获取课程json,则还需要设置semester.id
# e.g. semester.id=223


params = (('profileId', semester),)


def SaveCourseDatas(res_text):
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
    with open('./courses.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(dic, ensure_ascii=False))


def SaveCookies(cookies):
    with open('./cookies.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(cookies))


def LoadCookies():
    global cookies
    with open('./cookies.json') as f:
        try:
            json_data = json.load(f)
            cookies = json_data
        except JSONDecodeError:
            print("Empty file!")


def GetUserInfos(path="./user_info.secret"):
    '''
    返回字典
    {"Username":"...","Password":"..."}
    '''
    import os, re

    BASE_PATH = os.path.dirname(__file__)
    load_path = os.path.join(BASE_PATH, path)
    if not os.path.exists(load_path):
        raise Exception(f"No files found at {load_path}!")
    with open(load_path, "r") as f:
        line = f.readline()
        line_cnt = 1
        user_info = {}
        while line_cnt <= 1e5:
            if not line:
                break
            line = line.strip()
            username_match = re.match(r'Username\s*=\s*"(.+)"', line)
            password_match = re.match(r'Password\s*=\s*"(.+)"', line)

            if username_match:
                user_info['Username'] = username_match.group(1)
            if password_match:
                user_info['Password'] = password_match.group(1)
            if username_match and password_match:
                break
            line = f.readline()
            line_cnt += 1
    return user_info


def RefreshCookies():
    global cookies
    from browser_lauch import GetCookies

    usr_infos = GetUserInfos()
    cookie = GetCookies(usr_infos["Username"], usr_infos["Password"])
    cookies['JSESSIONID'] = cookie[1]
    cookies['srv_id'] = cookie[0]
    SaveCookies(cookies)


def GetUserDatas():
    # ua=UserAgent()
    # headers['User-Agent']=ua.random
    LoadCookies()
    if len(cookies) == 0:
        RefreshCookies()
    LoadCookies()
    return {
        'url': elect_url,
        'headers': headers,
        'cookies': cookies,
        'params': params,
        'data_uri': course_json_uri,
        'home_url': home_page_url,
        'root_url': root_url,
        'headers_json': headers_courseJson,
    }
