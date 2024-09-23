import requests
from user_datas import GetUserDatas, RefreshCookies, semester
import time


def get_data(url, headers, cookies, params=''):
    if params == '':
        response = requests.get(url=url, headers=headers, cookies=cookies)
    else:
        response = requests.get(
            url=url, headers=headers, cookies=cookies, params=params
        )

    return response


def GetCourses():

    user_data = GetUserDatas()
    headers = user_data['headers_json']
    cookies = user_data['cookies']
    params = user_data['params']
    cookies['semester.id'] = semester
    try:
        res = get_data(url=user_data['root_url'], headers=headers, cookies=cookies)

        if '登录' in res.text:
            RefreshCookies()
            res = get_data(user_data['home_url'], headers=headers, cookies=cookies)

        res = get_data(url=user_data['home_url'], headers=headers, cookies=cookies)

        res = get_data(
            url=user_data['data_uri'], headers=headers, cookies=cookies, params=params
        )
        if '出错了' in res.text:
            raise Exception
    except:
        res = get_data(
            url=user_data['data_uri'], headers=headers, cookies=cookies, params=params
        )
    from user_datas import SaveCourseDatas

    res.encoding = 'utf-8'
    data = res.text.strip('var lessonJSONs = ')
    data = data.strip(';')
    SaveCourseDatas(data)


def EleceCourse(id):
    user_data = GetUserDatas()
    url = user_data['url']
    headers = user_data['headers']
    cookies = user_data['cookies']
    data = {'optype': 'true', 'operator0': str(id) + ':true:0'}

    response = requests.post(url=url, headers=headers, cookies=cookies, data=data)

    if '账号登录' in response.text:
        RefreshCookies()

    user_data = GetUserDatas()
    url = user_data['url']
    headers = user_data['headers']
    cookies = user_data['cookies']
    data = {'optype': 'true', 'operator0': str(id) + ':true:0'}
    tp_url = f"https://eams.shanghaitech.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id={semester}"
    r1 = requests.get(url=tp_url, headers=headers, cookies=cookies)
    # print(r1.text)
    # time.sleep(1)
    response = requests.post(url=url, headers=headers, cookies=cookies, data=data)
    return response


# GetCourses()
