# import requests, time

# url = 'https://ids.shanghaitech.edu.cn/authserver/checkNeedCaptcha.htl'

# headers = {
#     "Accept": "application/json, text/javascript, */*; q=0.01",
#     "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
#     "Connection": "keep-alive",
#     "Sec-Fetch-Dest": "empty",
#     "Sec-Fetch-Mode": "cors",
#     "Sec-Fetch-Site": "same-origin",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
#     "X-Requested-With": "XMLHttpRequest",
#     "sec-ch-ua-mobile": "?0",
# }

# cookies = {
#     "Max-Age": "0",
#     # "route": "41879debaf20b4769e540e8b3e83ea5b",
#     # "JSESSIONID": "9727FC092B6E48D0B25FEAEFB4D72B62",
#     "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE": "zh_CN",
#     # "happyVoyage": "1lE3tdJTVDycfB3icqlV/2sN94vsuZ02G/fyXuB7UFaWUyg0x0Cbp5/XEIvC32TsA8z+cMriISu33gXLET/GeCvJEu4zk7G99v37JBA7X8qdTILSur65JcW++t673i9PliSCmvDpSob0vkw74peKBVA0HcAdkTZbPLjqGL60Bmc",
# }
# timestamp = time.time()
# timestamp = int(timestamp * 1000)
# params = {"username": "2023533176", "_": f"{timestamp}"}


# # 发送GET请求
# response = requests.get(url, headers=headers, cookies=cookies, params=params)

# print(response.text)

import requests, json

url = 'https://ids.shanghaitech.edu.cn/authserver/login'

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "null",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "sec-ch-ua-mobile": "?0",
}

cookies = {
    "Max-Age": "0",
    "route": "41879debaf20b4769e540e8b3e83ea5b",
    "JSESSIONID": "9727FC092B6E48D0B25FEAEFB4D72B62",
    "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE": "zh_CN",
    "happyVoyage": "1lE3tdJTVDycfB3icqlV/2sN94vsuZ02G/fyXuB7UFaWUyg0x0Cbp5/XEIvC32TsA8z+cMriISu33gXLET/GeCvJEu4zk7G99v37JBA7X8qdTILSur65JcW++t673i9PliSCmvDpSob0vkw74peKBVA0HcAdkTZbPLjqGL60Bmc",
}

data = {
    "username": "2023533176",
    "password": "YzwXy2wfQwwobB%2FsX16Mr0XJYv5XXXBSCnElODU8BHJW20S2PGwk%2BoG41L81MFP5dWuJFnBQr5e2IoO8AozCi98kq%2BD9t3578bZfrZMhNk4%3D",
    "captcha": "",
    "_eventId": "submit",
    "cllt": "userNameLogin",
    "dllt": "generalLogin",
    "lt": "",
    "execution": "46668a22-f6a9-4474-879e-4166e6bfd9c6_ZXlKaGJHY2lPaUpJVXpVeE1pSjkuMWlYR3RubWZKU1NoK0xUTGtnaC90b09iS3J4RnEwWUJ2V0tVS01XbWxyOWw2TlFRM2hFaU9hYXhSVDB0NmhJc1NXOVhIb1dySE5xS3lINUliRjlPYWhxSk1odjRQTHpBcjY1OFI2ZFlGbUVpZ1dyVE15RXJNTGxsUExoL1Jtc1Y0b3krbitzSnRUK3A0aXRZaWdBalJWMUVYL2lVaHp6c2xEdUhwaGROeHJzOUNmanpwWnl2S2FHczkxUnR3QzJLbHM4NXhYT0toQ2ZrMS9UaHRSMXBmKzMvb1gxZ2FwQVlxdFFvOUhzQll1RFR5QWQxYTJPQnQ1dW9hdE13L01KTUZyWlVqR2ZWVWkwZGFsVVYwd0o4UDdDSU9jaURyOWwwUk13enlXckhndzVxdzVidU5BRG4vZVFRN1N0ak9hSkZWMkZvMHZKZTNpN3NHM2VBWll3ZFBpZVJXcjhpY21MK2NBYnROM0hsVXBDM09CWURYRHB0ZDVpMnJNKzJaalBPSDdZczdVYlJOOXVPejRuazZlZnpibUdFQUxyYWFOMUZtVTR2YUV0NWJhb0d6RkdHOUFsbVBDM3pYOVNJenV3Q0lDTENFdW1QWlpieFhBaVI5L3g1eVR3VCtib2dPLzByU25hSEt5VUc0dm5nT0VDRi9IUmU3V2xFTWEwRFBzUzJWbTBlUUMrbVc0emhqaGNmeHd2QnpvcVFLeHBDajBIOXE4VmVPMEV1S3FheUdqTFNHdWt6L1VaaUFGWWhiTTlkbzdSQXJtbitIZkRiVTlZdUk4akUxL21rYmtKeVpkY2xFSmdMcWFDalRndndPczNXNXd6d3V1a2JjenRNT2o3aURZYTR6TmE5R3RpRElwSHlqVkVqc1hUdXlUcGwycXFNK0l0WGlsVC9UbkdMeENscDZ0QTRWRUFlaW1nUkNqcitxY0NlTG1NSXFRRzlRSHZhR05oVEJPbm91R09OcXpmRVdmWVZFWmJVb1pPK3R0aklvVjFNdTN6SHpYMVdERXZ6aGdkZjd6aWxqSmpFRWR0aW42OE15RzJqR0lEM2ZscFd6V3pBSmNsZm50OG51cnZVb3pZNWRmOUNHdzVWUmxUTTdUdU1qZWJBZm02eXZUMStWK1huYUQ1WTJkRWliSXNoS0ZybmtPUmNiUlZtdWwycVRoOG9zZUJCWjd3Y0FZTnk5OGZCbk9xc0poaFRMSWEvTzZXeUM0Y0M1dk9ZMFRqTm9KR1lvNCtPVDZvWm9pazFmNEYxQmRJWURGM2VCTFNpZ2hIaFU2UldqZGNFRUZzMnd1eVlwazJQSzQ1cHM3UGh2ZmtUdTdteWR2RGlZSUJZQnlsOUl2RUtPMmVQcUVPRmx5SnpBZUV4Rmp5NG5RSnJybGFTOXJEeDNUdkgwMG5uM3Fya3lvNjhEUEV0VWRLZnBvQ2lndkJJQWhTV0N4RTNMMnhnYmVRNDJ2LzlocGRIUStWemxYNzhpY09sWHlRU0hjdjZmQURjVVVvRlMvN0o3eWJ1ODZzeldNaXVGUTkyYnlDZFF6YzFuaTBqREFGOWhoS0pST1Ria21tdlRNNnZ5UWUxZVVZZ1BCdDR5cHdUcTkwLzhqOGZaRUkyQzZvdEVKdWUyakFBLzF1bERtSkEvaVFPMnc2Y0dUV3ZkWVM0ZDRTK0ZxYnFFS0kzaWZteEttRUhYbGttZnBmYVZ3WnNuK3BZa0pyRVFmbnlZMzBrbTYwUzMwL091TlRMUFNWSCs2WnRTYThFLzBveThVYTBITXYzQ210akQxSCtmL2xGOU9CSy9Cd2wya0gzYUN2dUQ2ZDF1N3RTbGUvMXVpQlh3eFNuY09mdmw4VDdRMkRJS2Zkb0t4N1BwMmIxTDdwVG9qRy8xb255Q25QVEFNU3ZHdmp4S28zU3hqZzJiTmNEdlU2Y1lkQmppQjlzR05SMDJlNjhxcUdXQXdJUHJmaWtFVk5NakxvYVRNeDZ2eEQzTkhnZ0RlSXVrTTlYaGRZUkFBU1hDSFRYWmFSUFVhSDBEMXlublhwdHdKVVc2MUNlQWNFeS84dDZCOFVVZmdCQnIwU0JDS3g0aWk0SXJTTTdqamw4K21pSkkrbzZWeWoyWUdwN0xkK3JTdzNhVjlFbUV3OUJYOUNnUjJBNTBCNzZOcFB6dzdIWTE4ZjVXU2pJR05yL3RaVWxLaXptdHdYcTI2UzIyY1FiYVJVME1XSHJjZ2tRbjRZQk5hdXZxZjczMURpeVBWb0pHSXlNZENGWlZOYjRuMC8xNFFPeXBSTFdJQ3pkWWY5d2ZrUDdDd2tlb2RLM01ITEpJcGFwUnhnaUJQOWtKbXY1YzdXbXpqdEJnV1dRWWtIdWhpSXgyREVlSXE2ZjlqUlVZSnBNQXhNT21CTW5ueTNZbUpmais1SjhjRjNmUnJpTkxDZHdhSUNtSU5QeU45WEgxSzdtZVNtUkNFVnFvQUZPM29rejBDRU9rTFNBNytFQ2dhZC85L1JvNXhGNDhreStOaklOMHlOaDdNd0lBUld4SWUwZGdTUisvSDNrR05ta3Ryb0F6ZUdoWVVYM3VOQ1RTbWZxcnhBS0l3b1IxN2NhS3lqV1FkR0xTZWljWGxOM2hqci9yeEo3ZStoaDRzZ09jTTB4MHB1RkpXUm01UURWejVXbkcrTHJxajkyQzVXRWZvV3llenhCYXFoYjY4TzBFdmJrd20xYWZ3R2ZkKzJCTGVOUnN1Qy9zVWowUEJjbFNRc0o5QkJBRGxKdlpyeThTWEhudkpzNVQxZVJCd042VkF0UGR6Z2x0aEthb001NEQvSDNkaUVOdm8vay9xelRtNTdKd01mbEw2aE96amQvdVVpK2hPZlVBQS90aDkrc01saFNDcEhCMmtDMGFrU2wvaC9RbHZ4Yi9KbWNOOHJQdStIc0drc0pRNEhjV2NSMGRtdE9XcmF0WGV4QTAxemdpbjVwNjhKNm1xSFVjUzRhYVNkcXJCWm5iN0luNitIV2hBdnlUYUxzNTdWSFJHUDNFVjBNcnBpQS94ZE9DaUN5dlpSc3d3SVFKcXdoRFpERWFoenZFTHVBcEpUSnlQcVUvbW9WQUZScnRaYUlMdUNVYXV3dHVpbEk5c0t4N2FiRm8wMzN6SW5NWi96NVRKUW1kN2JoZHQxU0lIb0FTUzF3d2pTNGZnM0xGT25sUjV4OXlRM3hyRThzVHAwNmh1a0hGdVkxMjFYeGlCR2FySG5qaGdlYlJKUmczTHd4UUJJeGJtTjFzYUhlR2kzYzVpV21uY1FRRjIxVGtQTHp1OFgyVDJVUFVUOGZ2d1p0aFFuODRwcUJpcUdqdTFvdFBPbXQ1ZS8xc1B4L1BwOXpsK0MwSkJvRGJhWUFxdGpnVGdzUFBwSkd6Mm1QRDN4ZHc0bWpGMlBUSldQZGF3UXdTbjF2by8yd2grZS9PSVJEL3VIbE1QRXl2blRsaE5DQjZkMjBQcjBXNk1aTU0xYVJOZEp1RXA0SDlNeThRUm9Sd0FySEpJS09xd2hlYjhxcnh1c3lmNHYza25YR0dKMjcxektMeVNFQk5JbkRFVGZYM0FkaldSalhzdHAwSUowTVVUcUZVNTU0eUNDYkQ0b2JNNUJXS2lYb1IxcktJSlRaVnlkRTFWYzhWeWEwSk1xOWRlRklrV0RaTzRzMDllb0tXdHhGWnFLdkUxRXFXYVVmOGpieFN2aE82bEJHUzgrNmtXN21VaFJZY2krZzFiNkR4WkROUllsaFp2T1JlNkJpd1EvQTBKUWpNT1ZWZGtIdFp6ZmRsSTRQdktLT3ZxMWRnTlMvcC9ienZ2MnRxM1EvUnlsSFlFTHpLdDIrV2dPTndmV3lhdmNaZjVvWHRGNjNRWTJBYzJKNFRZd0N4RzhaZnA1UDRCRDBqM0k0cnF2SzdUZVZ3cW5XUEZOellUY2RFN3VyTUxBSTdtMTRhSGpjdXptcEFGS3JWa3Z2WHFmU0dlazNYU1lwcDU1a1VaRDkrNk5tMVd3TFBndXcyaklXRUVzbWd0YzVHMjE1aG40bGllbFNlOHVKSlFyYm5aZ3hadEYwcSt5MmpiaURpaXg4S2R4UFZ4ZElRRkxvVXpqYXgvWGd1cnhUQWxyWmNWS2FLRk5ja2M0N205d0tEdDhVV3dxSnpRc3RiME5aYi9pWHFHenlIQTRuMGhpTE9jOEtxTFlDMnh6T3B0dU5TTzBkc0pHa00yZkZSSUJhWmhCekdhZVEyZHF1L3JBYit5ektmSzJZWktWMDNrMzZVcHlXRTRveUdYc3g1MzVVMEJDZDJqenFWRXdvSEJudlFVc2RiVDNlcHJTYk14ckFPcWt2NnZScEpmRXVXYUpXSTl1NXNjZlM0YUNOV3k3S2NrRXcwczhvZ1M5SzFNamdjcko3OXAraWtnZHY3c1RoWld4TlAvRVhrKzBJT241c21vTTJXdm5XMEtVN3gxS3NkLzRjVmZ1MVZZSXUwSm0yUzBheXpsNENQdVk2OCsyaDJ2bFhtTExNUW5RVG01bko3NGtkYUxWTjJCc3lORjdkdlpsYjhNUXE0cXRSWjEzNDJMQjAxRGZzdmpNaUw0RGpEbWdPSnRHYjN3dmZIbUNKeFp0dW9CeWdvOFhKSTVqeW0rdy80QWRkOWVLbDRKR3doZGhvbmUySTQ4dXQxcHljeE83OHhTanFqTzl6Y3lTalNRL0ZVNWRPTUdaWDl5bTNIWTF2TXA2Y0xvN29heW04eWI0WDU3N3ZJRzZzZzdFdlZySU52eGZZNm55RHFnQnlIdlMvQzRSZUtWdm1Zd3ZPRy9RMzBrajVIb2NKOTJ0MU9SZ3RFU3hqUjE1M0haWURhc3NBN2o4alhjRlJmSkwxbTlyWWE2Z0l4alRwVTdEbUVpUWhVcTNtOHg5ZG5kamhCNHVqMllPRThlNzdMQXhMWVdkdmZLYXNrRjdWMmtQWlBWUFhSNGpZTmI5c3RJamQyZy80dWVUblY5MExnVGYrazJOMFpZSGhWclBwYjhiWFNNeHgwM2tLcVEyWUtZWUVHMmtaUEN0bCt6MVFqQ05TSlJyeUUyU3N6OWVJNWFRZFc3ZityT3hPQit4bnp4dWRjVFk1M2JRZS8wbFdLWTljNTgwWWIvd0N3MW9QaTdkTFFJOGc3VlkwdS9BMmtOZHhsUXZwTFIwSU51T205TDZRR3BPaDNJZ1p3ZW9BMzRyWC9rREtuQ1dvMkdiYzA0NVZwQXVOclUrMFZJU3cvSmFOZnZCYkl3RGNQc1NtanRHMzFoK0NDUGZoOEZoRG13NmJwZ0ptbVpPKzVjaVd0OEpvOHdzSm5LNHBReC9oRjZ6SFJtM2pGekp6NzJ6Qkt0OFlKZ3VDQ0FCS0lpWHZjajBmWlVqd2J0U0dlMWo5S1ZiOGhPNWlxSWliU2lhWG11UjdtUnh6cXovOVJXOEd5MUQ5VENneGJZT1BxVjRoeHZDUC5GeHFta29ka2VpRXdWc3VjTWdQd3FjRmhFVnFEQ0M3Q2JaVzZHeVlBRXozMUw4RWEtclhDR0pLZzk3cHhRODNsMlFhS1FVdFRjaFNzM2FMQmVBM1JiZw%3D%3D",
}
data = json.dumps(data, separators=(',', ':'))
params = {"service": "https://egate-new.shanghaitech.edu.cn/login"}


# 发送GET请求
response = requests.post(
    url, headers=headers, cookies=cookies, data=data, params=params
)

print(response.text)
