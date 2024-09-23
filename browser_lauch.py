import selenium
from selenium import webdriver
from time import sleep
from user_datas import headers
from selenium.webdriver.common.by import By


def GetCookies(username: str, pwd: str):

    options = webdriver.ChromeOptions()

    browser = webdriver.Chrome(options=options)

    url = "https://eams.shanghaitech.edu.cn/eams/home!childmenus.action?menu.id=165"

    browser.get(url)
    sleep(3)

    username_input = browser.find_element(By.CSS_SELECTOR, "input[id='username']")
    pwd_input = browser.find_element(By.CSS_SELECTOR, "input[id='password']")
    username_input.send_keys(username)
    pwd_input.send_keys(pwd)

    btn = browser.find_element(By.CSS_SELECTOR, "[id='login_submit']")
    btn.click()
    sleep(1)
    cookies = browser.get_cookies()
    srv_id = cookies[0]['value']
    jession_id = cookies[1]['value']
    print(srv_id, jession_id)
    browser.quit()
    return [srv_id, jession_id]
